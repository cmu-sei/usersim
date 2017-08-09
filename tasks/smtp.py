# Ali Kidwai
# August 3, 2017
# Adapted from code written by Rotem Guttman

import base64
import random
import re
import smtplib
import sspi
import string

from email.mime.text import MIMEText
from loremipsum import get_sentence, get_paragraph
import pywintypes
import pythoncom
import win32com.client

from tasks import task

SMTP_EHLO_OKAY = 250
SMTP_AUTH_CHALLENGE = 334
SMTP_AUTH_OKAY = 235


class SMTP(task.Task):
    """ SMTP module for User Sim. Sends e-mails using SMTP. Uses SSL encryption and connects to an Exchange server if
    desired.
    """
    def __init__(self, config):
        """ Validates config and stores it as an attribute.
        """
        self._config = self.validate(config)

    def __call__(self):
        """ Generates a message and subject header if necessary, then sends an e-mail as specified in the config.
        """
        if not self._config['messages']:
            msgtext = get_paragraph()
        else:
            msgtext = random.choice(self._config['messages'])
        if not self._config['subjects']:
            subject = get_sentence(1)
        else:
            subject = random.choice(self._config['subjects'])
        self.sendmail(self._config['username'], random.choice(self._config['destinations']), self._config['site'],
                      msgtext, subject, self._config['encrypt'], self._config['exchange'])

    def cleanup(self):
        """ Doesn't need to do anything.
        """
        pass

    def stop(self):
        """ This task should be stopped after running once.

        Returns:
            True
        """
        return True

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        return str()

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {'required': {'username': 'str: E-mail address from which e-mails are sent, e.g. user@example.com',
                               'destinations': 'list: A list of e-mail addresses (strings) to send e-mails to. One will'
                                               ' be chosen at random.',
                               'site': 'str: Hostname of the e-mail server to use, with port optionally specified by a '
                                       'colon, e.g. "domain.org" or "domain.org:25". Port defalts to 25.'},
                  'optional': {'messages': 'list: A list of messages (strings) to form the body of an e-mail. One will '
                                           'be chosen at random. Default behavior is to randomly generate messages.',
                               'subjects': 'list: a list of subjects (strings) to form the subject of an e-mail. One '
                                           'will be chosen at random. Default behavior is to randomly generate subject '
                                           'headers.',
                               'exchange': 'bool: Whether to use exchange server authentication. Defaults to False.',
                               'encrypt': 'bool: Whether to use SSL encryption when connecting to the e-mail server. '
                                          'Defaults to False.'}}

        return params

    @classmethod
    def validate(cls, config):
        """ Validates the given configuration dictionary. Checks that string arguments have the correct type, but
        doesn't check if they are well-formed e-mail addresses, hostnames, etc.

        Args:
            config (dict): The dictionary to validate. Its keys and values are subclass-specific. Its values should
                be assumed to be str type and converted appropriately.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the config argument with missing optional parameters updated with default values.
        """
        if 'username' not in config:
            raise KeyError('username')
        if not isinstance(config['username'], str):
            raise ValueError('username: {} Must be a string'.format(str(config['username'])))

        if 'destinations' not in config:
            raise KeyError('destinations')
        if not isinstance(config['destinations'], list):
            raise ValueError('destinations: {} Must be a list of strings'.format(str(config['destinations'])))
        if not config['destinations']:
            raise ValueError('destinations: {} Must be non-empty'.format(str(config['destinations'])))
        for destination in config['destinations']:
            if not isinstance(destination, str):
                raise ValueError('destinations: {} Must be a list of strings'.format(str(config['destinations'])))

        if 'site' not in config:
            raise KeyError('site')
        if not isinstance(config['site'], str):
            raise ValueError('site: {} Must be a string'.format(str(config['site'])))
        if not config['site']:
            raise ValueError('site: {} Must be non-empty'.format(str(config['site'])))

        if 'messages' not in config:
            config['messages'] = list()
        if not isinstance(config['messages'], list):
            raise ValueError('messages: Must be a list of strings'.format(str(config['messages'])))
        for message in config['messages']:
            if not isinstance(message, str):
                raise ValueError('messages: Must be a list of strings'.format(str(config['messages'])))

        if 'subjects' not in config:
            config['subjects'] = list()
        if not isinstance(config['subjects'], list):
            raise ValueError('subjects: Must be a list of strings'.format(str(config['subjects'])))
        for subject in config['subjects']:
            if not isinstance(subject, str):
                raise ValueError('subjects: Must be a list of strings'.format(str(config['subjects'])))

        if 'exchange' not in config:
            config['exchange'] = False
        if not isinstance(config['exchange'], bool):
            raise ValueError('exchange: Must be a bool'.format(str(config['exchange'])))

        if 'encrypt' not in config:
            config['encrypt'] = False
        if not isinstance(config['encrypt'], bool):
            raise ValueError('encrypt: Must be a bool'.format(str(config['encrypt'])))

        return config

    def __asbase64(self, msg):
        return string.replace(base64.encodestring(msg), '\n', '')

    def __connect_to_exchange_as_current_user(self, smtp):
        """ Attempts to connect to an Exchange server.

        Args:
            smtp: The SMTP client session object

        Raises:
            smtplib.SMTPException: If server doesn't respond to commands as expected
        """
        # Send the SMTP EHLO command
        code, response = smtp.ehlo()
        if code != SMTP_EHLO_OKAY:
            raise smtplib.SMTPException("Server did not respond as expected to EHLO command")

        sspiclient = sspi.ClientAuth('NTLM')

        # Generate the NTLM Type 1 message
        sec_buffer=None
        err, sec_buffer = sspiclient.authorize(sec_buffer)
        ntlm_message = self.__asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 1 message -- Authentication Request
        code, response = smtp.docmd("AUTH", "NTLM " + ntlm_message)

        # Verify the NTLM Type 2 response -- Challenge Message
        if code != SMTP_AUTH_CHALLENGE:
            raise smtplib.SMTPException("Server did not respond as expected to NTLM negotiate message")

        # Generate the NTLM Type 3 message
        err, sec_buffer = sspiclient.authorize(base64.decodestring(response))
        ntlm_message = self.__asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 3 message -- Response Message
        code, response = smtp.docmd("", ntlm_message)
        if code != SMTP_AUTH_OKAY:
            raise smtplib.SMTPAuthenticationError(code, response)

    def sendmail(self, fromaddr, toaddr, site, msgtext, subject, encrypt, exchange):
        """ Constructs an e-mail message (a MIMEText object) and sends it to toaddr. Connects to an exchange server if
        desired.

        Args:
            fromaddr (str): The e-mail address from which the e-mail will be sent
            toaddr (str): The e-mail address to which the e-mail will be sent
            site (str): The hostname of the e-mail server
            msgtext (str): The body of the e-mail
            subject (str): The subject header of the e-mail
            encrypt (bool): Whether to use SSL encryption when connecting to the e-mail server
            exchange (bool): Whether to connect to an Exchange server
        """
        serverandport = site.split(':', 1)
        if len(serverandport) == 2:
            server = serverandport[0]
            port = int(serverandport[1])
        else:
            server = serverandport[0]
            port = 25
        msg = MIMEText(msgtext+'\n')
        msg['Subject'] = subject
        msg['From'] = fromaddr
        msg['To'] = toaddr
        if encrypt:
            s = smtplib.SMTP_SSL(server, port)
        else:
            s = smtplib.SMTP(server, port)
        if exchange:
            self.__connect_to_exchange_as_current_user(s)
        s.sendmail(fromaddr, toaddr, msg.as_string())
        s.quit()
