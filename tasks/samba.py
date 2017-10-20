# Ali Kidwai
# July 18, 2017
# Adapted from code written by Rotem Guttman and Joe Vessella
import os
import random
import time

from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

from tasks import task


class Samba(task.Task):
    """ Connects to and authenticates with a Samba share. Upload or download must be chosen per task config. If your
    share does not require authentication, you MUST set the appropriate permission bits on the shared folder so that
    guests can upload files to it!
    """
    def __init__(self, config, debug=False):
        self._config = config
        self._smb_con = None
        self._debug = debug

    def __call__(self):
        self._smb_connect(self._config['address'], self._config['port'],
                          self._config['user'], self._config['password'])

        if not self._config['files']:
            self._echo()
        elif self._config['upload']:
            self._upload()
        else:
            self._download()

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
        return ''

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {'required': {'address': 'str| the Samba server address'},
                  'optional': {'port': 'int| the port for the Samba server. Defaults to 445',
                               'user': 'str| a username to authenticate with the server if necessary',
                               'password': 'str| password for user',
                               'upload': 'bool| True to use the files parameter as a list of local files to upload, '
                                         'False to use the files parameter as a list of remote files to download. '
                                         'Default False',
                               'files': '[str]| a list of file paths (strings) to download from the Samba share if '
                                        'upload is False, otherwise a list of local paths to upload. If not '
                                        'specified, the task will send SMB Echo requests with random strings instead. '
                                        'It is best to use forward slashes (/) to specify paths, even on Windows',
                               'write_dir': 'str| A writeable path. If upload is False, then this is a local path in '
                                            'which files will be downloaded. If upload is True, then this is a remote '
                                            'path (including the share name) on the remote Samba server. If not '
                                            'specified, then downloads will not save downloaded files to the disk, and'
                                            'uploads will not be attempted. It is best to use forward slashes (/) even '
                                            'for Windows paths.'}}
        return params

    @classmethod
    def validate(cls, config):
        """ Validates the given configuration dictionary.

        Args:
            config (dict): The dictionary to validate. See parameter() for required format.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the conf_dict argument with missing optional parameters added with default values.
        """
        if 'address' not in config:
            raise KeyError('address')
        if not isinstance(config['address'], str):
            raise ValueError('address: {} Must be a string'.format(str(config['address'])))

        if 'port' not in config:
            config['port'] = 445
        if not isinstance(config['port'], int):
            raise ValueError('port: {} Must be an int'.format(str(config['port'])))
        if config['port'] < 0 or config['port'] > 65535:
            raise ValueError('port: {} Must be in the range [0, 65535]'.format(str(config['port'])))

        if 'user' not in config:
            config['user'] = ''
        if not isinstance(config['user'], str):
            raise ValueError('user: {} Must be a string'.format(str(config['user'])))

        if 'password' not in config:
            config['password'] = ''
        if not isinstance(config['password'], str):
            raise ValueError('password: {} Must be a string'.format(str(config['password'])))

        if 'upload' not in config:
            config['upload'] = False

        if 'files' not in config:
            config['files'] = []
        if not isinstance(config['files'], list):
            raise ValueError('files: {} Must be a list of strings'.format(str(config['files'])))
        for file in config['files']:
            if not isinstance(file, str):
                raise ValueError('files: {} Must be a list of strings'.format(str(config['files'])))

        if 'write_dir' not in config:
            config['write_dir'] = ''
        if not isinstance(config['write_dir'], str):
            raise ValueError('write_dir: {} Must be a string'.format(str(config['write_dir'])))

        return config

    def _echo(self):
        """ Send an echo request to the server with a randomly-generated string.
        """
        length = random.randint(1, 100)
        data = ''

        for _ in range(length):
            data += random.choice('abcdefghijklmnopqrstuvwxyz')

        self._smb_con.echo(data)

    def _download(self):
        """ Retrieves a list of files. Will make an attempt to retrieve all files. If any files fail to retrieve, raises
        an exception at the end.

        Raises:
            Exception: If any file retrieval fails, an exception will be raised whose message includes a list of all
                failures.
        """
        file_paths = self._config['files']
        failures = []

        for file_path in file_paths:
            try:
                self._retrieve_file(file_path)
            except Exception as e:
                failures.append(file_path + ': ' + str(e))
        if failures:
            raise Exception('Failed to retrieve the following files:\n%s' % '\n'.join(failures))

    def _upload(self):
        """ Tries to upload a list of files to the server. Will make an attempt to upload all files in the list, using
        the local path as the remote path. If any file fails to upload, raises an exception at the end.

        Args:
            file_paths (list): A list of local files to upload to the server. Files will be uploaded in the order given.
                Files should use forward slashes (/) even for Windows paths.

        Raises:
            Exception: If any file upload fails, an exception will be raised whose message includes a list of all
                failures.
        """
        file_paths = self._config['files']
        failures = []

        for file_path in file_paths:
            try:
                self._write_file(file_path)
            except Exception as e:
                failures.append(file_path + ': ' + str(e))
        if failures:
            raise Exception('Failed to retrieve the following files:\n%s' % '\n'.join(failures))

    def _retrieve_file(self, remote_path):
        """ Retrieve remote_path and save it at the configured 'write_dir' folder if it is specified, otherwise black
        hole the downloaded file data.

        Args:
            remote_path (str): The path to the file to retrieve.
        """
        write_dir = self._config['write_dir']
        if os.path.isdir(write_dir):
            out_file = os.path.join(write_dir, os.path.basename(remote_path))
        else:
            out_file = os.devnull

        try:
            share, path = remote_path.split('/', 1)
        except ValueError:
            raise ValueError('A path to a file must be specified along with the share name.')

        with open(out_file, 'wb') as f:
            if self._debug:
                print('Attempting to retrieve file %s' % os.path.join(share, path))
            self._smb_con.retrieveFile(share, path, f)

    def _write_file(self, local_path):
        """ Write the file at local_path to the directory in the 'write_path' config dict.

        Args:
            local_path (str): A path to a local file to upload to the server.
        """
        write_dir = self._config['write_dir']
        if not write_dir:
            # As noted in parameters, if this isn't specified then we're not uploading. Finding a writeable shared
            # folder seems pretty tough to make reliable.
            return

        try:
            share, path = write_dir.split('/', 1)
        except ValueError:
            share, path = write_dir, ''

        path = os.path.join(path, os.path.basename(local_path))

        with open(local_path, 'rb') as f:
            if self._debug:
                print('Attempting to upload file %s' % local_path)
            self._smb_con.storeFile(share, path, f)

    def _smb_connect(self, address, port, username, password):
        """ Attempts to connect to the Samba server at address. Will try direct TCP first. If that fails, tries not
        using direct TCP.

        Args:
            address (str): The address of the Samba server
            port (int): Port for the Samba server
            username (str): The username to log in with
            password (str): The password for username
        """
        try:
            # Need to provide *A* remote name it seems, but the share doesn't seem too particular about what it is.
            # If the remote server is using direct TCP this flag must be set to True or we get an exception when we try
            # to connect.
            self._smb_con = SMBConnection(username, password, '', 'usersim', is_direct_tcp=True)
            self._smb_con.connect(address, port)
        except Exception:
            self._smb_con = SMBConnection(username, password, '', 'usersim')
            self._smb_con.connect(address, port)
