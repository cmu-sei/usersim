# Ali Kidwai
# June 16, 2017
# Adapted from code written by Rotem Guttman and Joe Vessella

import ftplib
import time

from tasks import task


class FTP(task.Task):
    """ FTP module for UserSim. Connects to and authenticates with an FTP server, then attempts to download a file.
    """
    def __init__(self, config):
        """ Validates config and stores it as an attribute.
        """
        self._config = self.validate(config)

    def __call__(self):
        """ Connects to the ftp server as specified in config and attempts to download file from server.
        """
        self.retrieveFile(self._config['site'], self._config['file'], self._config['user'], self._config['password'])

    def cleanup(self):
        """ Doesn't need to do anything
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
        params = {'required': {
                    'site': 'str: ftp server to access',
                    'file': 'str: Name of file to download'},
                  'optional': {
                    'user': 'str: user to log in with. Defaults to "anonymous"',
                    'password': 'str: password to log in with. If user is "anonymous", password defaults to '
                                '"anonymous@". If user is not "anonymous", defaults to empty string.'}}
        return params

    @classmethod
    def validate(cls, config):
        """ Validates the given configuration dictionary. Makes sure that config['site'] and config['file'] are strings,
        but does not actually check if they are valid site/filenames.

        Args:
            config (dict): The dictionary to validate. See parameters() for required format.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the config argument, updated with default values for missing optional keys.
        """
        for key in ['site', 'file']:
            if key not in config:
                raise KeyError(key)

        if not isinstance(config['site'], str):
            raise ValueError('site: {} Must be a string'.format(str(config['site'])))
        if not config['site']:
            raise ValueError('site: {} Must be non-empty'.format(config['site']))
        if not isinstance(config['file'], str):
            raise ValueError('file: {} Must be a string'.format(str(config['file'])))
        if not config['file']:
            raise ValueError('file: {} Must be non-empty'.format(config['file']))

        if 'user' not in config:
            config['user'] = 'anonymous'
            config['password'] = 'anonymous@'
        if 'password' not in config:
            config['password'] = str()

        return config

    def retrieveFile(self, server, filename, user, password):
        """ Attempts to download filename from server using user and password to log in if necessary.

        Args:
            server (str): Name of ftp server to connect to
            filename (str): Name of file to download
            user (str): Username to log in with
            password (str): Password for user

        Raises:
            RuntimeError: If the file download is unsuccessful
        """
        try:
            ftp = ftplib.FTP(server, user, password)
            ftp.retrbinary('RETR ' + filename, open(filename, 'wb').write)
            ftp.quit()
        except:
            raise RuntimeError('Unable to read file from FTP server')
