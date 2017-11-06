# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import os
import platform
import random
import re
import subprocess
import time

try:
    import pythoncom
    import win32com.client
except ImportError:
    # Tasks must be importable on any platform.
    pass

import api
from tasks import task


class SharedOutlook(object):
    outlook_application = None
    mapi_namespace = None
    redemption_session = None
    mapi_utils = None

    def __new__(cls):
        pythoncom.CoInitialize()

        if not cls.outlook_application:
            try:
                cls.outlook_application = win32com.client.gencache.EnsureDispatch('Outlook.Application')
                cls.mapi_namespace = cls.outlook_application.GetNamespace('MAPI')
                cls.redemption_session = win32com.client.dynamic.Dispatch('Redemption.RDOSession')
                cls.mapi_utils = win32com.client.Dispatch('Redemption.MAPIUtils')
                cls.redemption_session.Logon()
            except Exception:
                # Ensure that it's all or none.
                cls.clear()
                raise

        # These must ALL be initialized by now - if not this is a failure.
        assert cls.outlook_application and cls.mapi_namespace and cls.redemption_session and cls.mapi_utils

        return cls

    @classmethod
    def clear(cls):
        cls.outlook_application = None
        cls.mapi_namespace = None
        cls.redemption_session = None
        cls.mapi_utils = None

class Outlook(task.Task):
    """ Interacts with Outlook for reading emails. Regular expressions can be used to react to email content. Requires
    Outlook and OutlookRedemption to be installed. Windows-only.
    """
    def __init__(self, config):
        if not platform.system() == 'Windows':
            raise OSError('This task is only compatible with Windows.')
        self._config = config
        self._outlook = SharedOutlook()
        # Compile all the regexes since they will be checked on each message.
        self._regexes = {re.compile(regex): config['regexes'][regex] for regex in config['regexes']}

    def __call__(self):
        if self._config['nuke_outlook']:
            self._nuke_folders()

        self._check_messages()

    def cleanup(self):
        pass

    def stop(self):
        return True

    def status(self):
        return ''

    def _nuke_folders(self):
        DEFAULTS = ['Inbox', 'Deleted Items', 'Outbox', 'Drafts', 'Sent Items', 'RSS Feeds']

        folders = self._config['nuke_folders']
        if not folders:
            folders = DEFAULTS

        for folder in folders:
            try:
                folder_obj = self._outlook.redemption_session.GetFolderFromPath(folder)
                folder_obj.EmptyFolder(True)
            except Exception:
                raise Exception('Could not find folder to nuke: {}'.format(folder))

    def _check_messages(self):
        """ Interact with Outlook depending upon configuration.
        """
        self._exchange_check()

        # Inbox.
        folder = self._outlook.mapi_namespace.GetDefaultFolder(win32com.client.constants.olFolderInbox)
        self._process_folder(folder)

        # Junk.
        folder = self._outlook.mapi_namespace.GetDefaultFolder(win32com.client.constants.olFolderJunk)
        self._process_folder(folder)

        # Empty contents of the Deleted folder.
        if self._config['delete_handled']:
            folder = self._outlook.redemption_session.GetFolderFromPath('Deleted Items')
            folder.EmptyFolder(True)

    def _exchange_check(self):
        """ Check if we failed to connect to Exchange.
        """
        mode = self._outlook.redemption_session.ExchangeConnectionMode

        if mode not in [800, 700, 60, 500, 0]:
            # 0 indicates that exchange is not configured, but may not be fatal.
            if value == 400:
                # Disconnected, using cached mode.
                reason = 'Outlook in cached mode because Exchange is disconnected.'
            elif value == 300:
                # Exchange disconnected.
                reason = 'Outlook unusable because Exchange is disconnected.'
            elif value in [200, 100]:
                # Outlook in Work Offline mode.
                reason = 'Outlook unusable because it is in Work Offline mode.'
            else:
                reason = 'Outlook connection mode value is not known: {}'.format(str(mode))

            # All of these are fatal - clear the references and we can try again next time and hope for the best.
            self._outlook.clear()
            raise Exception(reason)

    def _process_folder(self, folder):
        """ Walk through the messages in the given folder and handle them based on configuration.

        Args:
            folder (MAPI folder object): The folder to walk through.
        """
        # Give Outlook a bit of time to breathe and contemplate its meaningless existence.
        time.sleep(1)
        # Since we want it to look shiny...
        folder.Display()
        time.sleep(1)

        item_store = folder.Items
        message = item_store.GetFirst()
        delete_after = []
        handled_messages = 0

        while message:
            handled_messages += 1
            if not self._config['unread'] or message.UnRead:
                # Redemption gets around some Outlook API security restrictions.
                redemption_item = win32com.client.Dispatch('Redemption.SafeMailItem')
                redemption_item.Item = message

                # TODO: Check if the following is used - original used a continue without advancing the iter, meaning
                # this would have been an infinite loop if it was encountered.
                if message.Class != win32com.client.constants.olMail:
                    # Not a message, so we'll just skip it.
                    if self._config['delete_handled']:
                        delete_after.append(message)
                    message = item_store.GetNext()
                    continue

                if self._config['display_messages']:
                    message.Display()

                self._check_regexes(redemption_item.Body)
                self._check_links(redemption_item.Body)
                self._check_attachments(redemption_item.Attachments)

                if self._config['display_messages']:
                    # 0 saves changes, 1 discards.
                    message.Close(0)

                if self._config['delete_handled']:
                    delete_after.append(message)

                message.UnRead = False
                message.Save()

            message = item_store.GetNext()

        # Clear out messages marked for deletion earlier - this is separate in order to avoid messing with order while
        # in the loop.
        for message in delete_after:
            message.Delete()

        # Try to close any extra open explorer windows.
        # TODO: Check if this is working.
        explorer_count = len(self._outlook.outlook_application.Explorers)
        if explorer_count > 1:
            # MS Program APIs are 1-indexed.
            for i in range(2, explorer_count + 1):
                try:
                    self._outlook.outlook_application.Explorers[i].Close()
                except Exception:
                    continue

    def _check_regexes(self, body):
        """ Check if any of the configured regexes match against an email.

        Args:
            body (str): The string of an email body.
        """
        for regex in self._regexes:
            if regex.search(body):
                api.new_task(self._regexes[regex])

    def _check_links(self, body):
        """ Check if a link exists in an email, and if so checks if we should open it.

        Args:
            body (str): The string of an email body.
        """
        # As useful as they are, regular expressions are ugly. If the name doesn't give it away, this matches a URL.
        url_regex = '([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|(((news|telnet|nttp|file|http|ftp|https)://)' \
                    '|(www|ftp)[-A-Za-z0-9]*\\.)[-A-Za-z0-9/\\.]+)(:[0-9]*)?'
        match = re.search(url_regex, body)

        if match and random.randint(1, 100) <= self._config['open_links']:
            # There was a link in the email and we chose to click it.
            link_config = {'type': 'firefox', 'config': {'sites': [match.group()]}}
            api.new_task(link_config)

    def _check_attachments(self, attachments):
        """ Check if we should open attachments, and if so, save and open all attachments.
        """
        if random.randint(1, 100) <= self._config['open_attachments']:
            for i in range(attachments.Count):
                # Microsoft uses 1-indexed collections. Of course they do.
                item = attachments.Item(i + 1)
                path = os.path.expanduser('~') + os.sep + item.FileName

                item.SaveAsFile(path)
                # Quotes below are single-double-single.
                subprocess.Popen('"' + path + '"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    @classmethod
    def parameters(cls):
        """ Information about this task's configuration.

        Returns:
            dict: With keys 'required' and 'optional', whose values are dicts with the task's required and optional
                config keys, and whose values are human-readable strings giving information about that key.
        """
        config = {}

        required = {}

        optional = {'unread': 'bool| Read only unread messages if True, otherwise read all messages. (default True)',
                    'open_links': 'int| Percent chance to open any given link. (default 0)',
                    'open_attachments': 'int| Percent chance to open any attachment. (default 0)',
                    'delete_handled': 'bool| Delete handled emails if True, otherwise do not delete. (default False)',
                    'display_messages': 'bool| Display messages visually if True, otherwise do not. (default False)',
                    'nuke_outlook': 'bool| Empty Outlook folders if True, otherwise do not. (default False)',
                    'nuke_folders': '[str]| If nuke_outlook is True, specifies a list of folders to empty. Optional'
                                    ' even when nuke_outlook is True. If nuke_outlook is False, this does nothing.',
                    'regexes': '{str: task}| A dictionary mapping a regular expression string to a Task '
                               'configuration. If the regex finds a match in an email, the associated task is spawned.'}

        config['required'] = required
        config['optional'] = optional

        return config

    @classmethod
    def validate(cls, config):
        """ Validate the task configuration.

        Raises:
            KeyError: If a required key is missing
            ValueError: If a key's value does not make sense.

        Returns:
            dict: The given configuration with missing optional keys filled in with default values.
        """
        defaults = {'unread': True,
                    'open_links': 0,
                    'open_attachments': 0,
                    'delete_handled': False,
                    'display_messages': False,
                    'nuke_outlook': False,
                    'nuke_folders': [],
                    'regexes': {}}

        config = api.check_config(config, cls.parameters(), defaults)

        open_links = config['open_links']
        open_attachments = config['open_attachments']

        # 101 because the upper bound is exclusive.
        if open_links not in range(101):
            raise ValueError('open_links: {} Must be between 0 and 100.'.format(str(open_links)))
        if open_attachments not in range(101):
            raise ValueError('open_attachments: {} Must be between 0 and 100.'.format(str(open_attachments)))

        regexes = config['regexes']
        for regex in regexes:
            try:
                # Test that this is a valid regex - regex correctness can't be tested and is up to the user.
                re.compile(regex)
            except Exception:
                raise ValueError('regexes: {} Is not a valid regular expression.'.format(str(regex)))

        return config

    @staticmethod
    def _get_email_host(address):
        """ Attempts to fetch just the hostname part of the email address.

        Args:
            address (str): An email address.

        Returns:
            str or None: The hostname portion of address if it can be parsed, otherwise None.
        """
        match = re.search('@.*\.', address)
        if match:
            return match.group()[1:]
