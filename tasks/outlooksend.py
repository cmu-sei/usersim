import platform

try:
    import win32com.client
except ImportError:
    # Tasks must be importable on any platform.
    pass

from tasks import outlook


class OutlookSend(outlook.Outlook):
    """ Interact with Outlook to send emails. Requires Outlook and OutlookRedemption to be installed. Windows-only.
    """
    def __init__(self, config):
        if not platform.system() == 'Windows':
            raise OSError('This task is only compatible with Windows.')

        self._config = config
        self._outlook = outlook.SharedOutlook()

    def __call__(self):
        self._send_message()

    def _send_message(self):
        subject, body = self._get_content()

        # Attempted workaround for emails sitting in Outbox. May not actually work correctly.
        if self._outlook.outlook_application.Explorers.Count == 0:
            folder = self._outlook.mapi_namespace.GetDefaultFolder(win32com.client.constants.olFolderOutbox)
            folder.Display()

        self._exchange_check()

        # TODO: Make sure new order works.
        outbox = self._outlook.mapi_namespace.GetDefaultFolder(win32com.client.constants.olFolderOutbox)
        outlook_mail_item = self._outlook.outlook_application.CreateItem(win32com.client.constants.olMailItem)
        outlook_mail_item = outlook_mail_item.Move(outbox)

        outlook_mail_item.Subject = subject
        outlook_mail_item.Body = body
        outlook_mail_item.Save()

        for file_ in self._config['attachments']:
            outlook_mail_item.Attachments.Add(file_)

        # Need to use Redemption to actually get it to send correctly.
        new_email = win32com.client.Dispatch('Redemption.SafeMailItem')
        new_email.Item = outlook_mail_item
        new_email.Recipients.Add(self._config['destination'])
        new_email.Recipients.ResolveAll()
        new_email.Send()

    def _get_content(self):
        """ Get subject and body.

        Returns:
            str, str: First return value is email subject and second value is email body.
        """
        if self._config['dynamic']:
            subject = 'DYNAMIC OPTION NOT YET IMPLEMENTED'
            body = 'DYNAMIC OPTION NOT YET IMPLEMENTED'
        else:
            subject = self._config['subject']
            body = self._config['body']

        return subject, body

    @classmethod
    def parameters(cls):
        """ Information about this task's configuration.

        Returns:
            dict: With keys 'required' and 'optional', whose values are dicts with the task's required and optional
                config keys, and whose values are human-readable strings giving information about that key.
        """
        config = {}

        required = {'username': 'str| The "From" address.',
                    'destination': 'str| The "To" address.',
                    'subject': 'str| Subject line. Specify empty string if optional parameter "dynamic" is used.',
                    'body': 'str| Message body. Specify empty string if optional parameter "dynamic" is used.'}

        optional = {'attachments': '[str]| A list of paths to files that should be attached.',
                    'dynamic': 'bool| Generate subject and body. Default False.'}


        config['required'] = required
        config['optional'] = optional

        return config

    @classmethod
    def validate(cls, config):
        """ Validate the task configuration.

        Raises:
            KeyError: If a required key is missing.
            ValueError: If a key's value is not valid.
        """
        defaults = {'attachments': [],
                    'dynamic': False}
        config = api.check_config(config, cls.parameters(), defaults)

        return config
