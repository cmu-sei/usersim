# Ali Kidwai
# August 3, 2017
# Adapted from code written by Rotem Guttman
import base64
from email.mime.text import MIMEText
import random
import smtplib

from tasks import task


class SMTP(task.Task):
    """ SMTP module for User Sim. Sends e-mails using SMTP. Uses SSL encryption and connects to an Exchange server if
    desired.
    """
    def __init__(self, config):
        self._config = config

    def __call__(self):
        """ Generates a message and subject header if necessary, then sends an e-mail as specified in the config.
        """
        if not self._config['messages']:
            body = str()
            for _ in range(random.randint(1, 200)):
                body += random.choice('abcdefghijklmnopqrstuvwxyz')
        else:
            body = random.choice(self._config['messages'])

        if not self._config['subjects']:
            subject = str()
            for _ in range(random.randint(1, 50)):
                subject += random.choice('abcdefghijklmnopqrstuvwxyz')
        else:
            subject = random.choice(self._config['subjects'])

        self.send_mail(body, subject)

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
        params = {'required': {'email_addr': 'str: E-mail address from which e-mails are sent, e.g. user@example.com',
                               'destinations': 'list: A list of e-mail addresses (strings) to send e-mails to. One will'
                                               ' be chosen at random.',
                               'mail_server': 'str: Hostname of the e-mail server to use, with port optionally '
                                              'specified by a '
                                       'colon, e.g. "domain.org" or "domain.org:25". Port defalts to 25.'},
                  'optional': {'messages': 'list: A list of messages (strings) to form the body of an e-mail. One will '
                                           'be chosen at random. Default behavior is to randomly generate messages.',
                               'subjects': 'list: a list of subjects (strings) to form the subject of an e-mail. One '
                                           'will be chosen at random. Default behavior is to randomly generate subject '
                                           'headers.',
                               'encrypt': 'bool: Whether to use SSL encryption when connecting to the e-mail server. '
                                          'Defaults to False.',
                               'port': 'int: Mail server port. Default is 25.'}}

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
        if 'email_addr' not in config:
            raise KeyError('email_addr')
        if not isinstance(config['email_addr'], str):
            raise ValueError('email_addr: {} Must be a string'.format(str(config['email_addr'])))

        if 'destinations' not in config:
            raise KeyError('destinations')
        if not isinstance(config['destinations'], list):
            raise ValueError('destinations: {} Must be a list of strings'.format(str(config['destinations'])))
        if not config['destinations']:
            raise ValueError('destinations: {} Must be non-empty'.format(str(config['destinations'])))
        for destination in config['destinations']:
            if not isinstance(destination, str):
                raise ValueError('destinations: {} Must be a list of strings'.format(str(config['destinations'])))

        if 'mail_server' not in config:
            raise KeyError('mail_server')
        if not isinstance(config['mail_server'], str):
            raise ValueError('mail_server: {} Must be a string'.format(str(config['mail_server'])))
        if not config['mail_server']:
            raise ValueError('mail_server: {} Must be non-empty'.format(str(config['mail_server'])))

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

        if 'encrypt' not in config:
            config['encrypt'] = False
        if not isinstance(config['encrypt'], bool):
            raise ValueError('encrypt: Must be a bool'.format(str(config['encrypt'])))

        if 'port' not in config:
            config['port'] = 25
        if not isinstance(config['port'], int):
            raise ValueError('port: Must be an int'.format(str(config['port'])))

        return config

    def _asbase64(self, message):
        return str.replace(base64.encodestring(message), '\n', '')

    def send_mail(self, body, subject):
        """ Constructs an e-mail message (a MIMEText object) and sends it to toaddr. Connects to an exchange server if
        desired.

        Args:
            body (str): The body of the e-mail
            subject (str): The subject header of the e-mail
        """
        server = self._config['mail_server']
        port = self._config['port']
        from_addr = self._config['email_addr']
        to_addr = random.choice(self._config['destinations'])

        message = MIMEText(body + '\n')
        message['Subject'] = subject
        message['From'] = from_addr
        message['To'] = to_addr

        if self._config['encrypt']:
            s = smtplib.SMTP_SSL(server, port)
        else:
            s = smtplib.SMTP(server, port)

        s.sendmail(from_addr, to_addr, message.as_string())
        s.quit()
