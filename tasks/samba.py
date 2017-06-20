import os
import random
from loremipsum import get_paragraph
from smb.SMBConnection import SMBConnection
from smb.smb_structs import OperationFailure

from tasks import task

class Samba(task.Task):
    def __init__(self, config, debug=False):
        """ Validates config and stores it as an attribute. Also initializes self._smb_con to None.
        """
        self._config = self.validate(config)
        self._smb_con = None
        self._debug = debug

    def __call__(self):
        """ Establish a connection with the Samba server. If files have been specified, download them from the Samba.
        Otherwise, upload or download a random a file.
        """
        self._smb_connect(self._config['address'], self._config['port'],
                          self._config['user'], self._config['passwd'])
        if self._config['files']:
            self.retrieve_files(self._config['files'])
        else: # No files specified; upload/download a random file
            if random.getrandbits(1): # Flip a coin
                self.retrieve_random_file()
            else:
                self.upload_random_file()

    def cleanup(self):
        """ Doesn't need to do anything
        """
        return None

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
        return ""

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {'required': {'address': 'str: the Samba server address'},
                  'optional': {'port': 'int: the port for the Samba server. Defaults to 445',
                               'user': 'str: a username to authenticate with the server if necessary',
                               'passwd': 'str: password for user',
                               'files': 'list: a list of filenames to download from the Samba share. If not specified, '
                                        'the UserSim will either upload or download a random file.'}}
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

        if 'passwd' not in config:
            config['passwd'] = ''
        if not isinstance(config['passwd'], str):
            raise ValueError('passwd: {} Must be a string'.format(str(config['passwd'])))

        if 'files' not in config:
            config['files'] = []
        if not isinstance(config['files'], list):
            raise ValueError('files: {} Must be a list of strings'.format(str(config['files'])))
        for file in config['files']:
            if not isinstance(file, str):
                raise ValueError('files: {} Must be a list of strings'.format(str(config['files'])))

        return config

    def retrieve_files(self, file_paths):
        """ Retrieves a list of files. Will make an attempt to retrieve all files. If any files fail to retrieve, raises
        an exception at the end.

        Args:
            file_paths (list): A list of files to retrieve from the server. Files will be retrieved in the order given.
                The file paths may use forward slashes or backslashes as separators.

        Raises:
            Exception: If any file retrieval fails, an exception will be raised whose message includes a list of all
                failures.
        """
        failures = []
        for file_path in file_paths:
            file_path.replace('\\', '/')
            share, path = file_path.split('/', 1)
            try:
                self._retrieve_file(share, path)
            except OperationFailure as e:
                failures.append(file_path + ' ' + e.message)
        if failures:
            raise Exception('Failed to retrieve the following files:\n%s' % '\n'.join(failures))

    def retrieve_random_file(self):
        """ Attempts to download a random file from the remote Samba server. A best-effort attempt is made.
        """
        chosen_share = self._choose_new_share()
        chosen_path = ''
        path_is_dir = True

        while path_is_dir:
            files = self._smb_con.listPath(chosen_share, chosen_path)
            try:
                # Don't include the special files . and ..
                chosen_file = random.choice(files[2:])
            except IndexError as e:
                # TODO: This is the super lazy way. Otherwise we'd need to keep track of each directory we visit.
                # Maybe when I have some time available.
                raise Exception('Share %s appears to be completely empty or has an empty directory.' % chosen_share)

            path_is_dir = chosen_file.isDirectory
            chosen_path = os.path.join(chosen_path, chosen_file.filename)

        self._retrieve_file(chosen_share, chosen_path)

    def upload_random_file(self):
        """ Attempts to create a file on a random share on the Samba server. This is a best-effort attempt.
        """
        chosen_share = self._choose_new_share()
        file_name = str(random.randint(0, 999)) + '.txt'
        self._write_file(chosen_share, file_name, get_paragraph())

    def _choose_new_share(self):
        """ Pick one of the shared devices on the server at random.

        Raises:
            OperationFailure: If a valid share is unable to be found.

        Returns:
            str: The name of the chosen share.
        """
        # There are a bunch of special "shares" returned by this call which are not valid. Hopefully this can trim down 
        # the occurence of trying to use those.
        shares = []
        for share in self._smb_con.listShares():
            if share.name[-1] != '$':
                shares.append(share.name)
        random.shuffle(shares)

        if self._debug:
            print('Found the following shares: %s' % shares)

        while shares:
            chosen_share = shares.pop()
            try:
                # Make sure the share is accessible
                if self._debug:
                    print('Trying share %s' % chosen_share)
                self._smb_con.listPath(chosen_share, '')
            except OperationFailure as e:
                if self._debug:
                    print('Failed to access %s' % chosen_share)
            else:
                if self._debug:
                    print('Chose share %s' % chosen_share)
                return chosen_share

        raise Exception('Could not find a valid share to use.')

    def _retrieve_file(self, share, path):
        """ Retrieve the file at path from share.
        """
        if self._debug:
            out_file = 'smbdebug'
        else:
            out_file = os.devnull

        with open(out_file, 'w') as f:
            if self._debug:
                print('Attempting to retrieve file %s' % os.path.join(share, path))
            self._smb_con.retrieveFile(share, path, f)

    def _write_file(self, share, path, content):
        """ Write a file containing content at path in share.
        """
        class FileLike(object):
            """ This is needed because the Samba library only supports uploading using file-like objects with a read 
            method.
            """
            def __init__(self, content):
                self.text = content
                self._read = False

            def read(self, _):
                if not self._read:
                    self._read = True
                    return self.text
                else:
                    return ''

        f = FileLike(str(content))
        self._smb_con.storeFile(share, path, f)

    def _smb_connect(self, address, port, username, password):
        """ Attempts to connect to the Samba server at address. Will try direct TCP if initial attempt fails.
        """
        try:
            self._smb_con = SMBConnection(username, password, '', 'usersim') # TODO: Ask Joe if this should be hardcoded
            self._smb_con.connect(address, port)
        except Exception:
            # If the remote server is using direct TCP this flag must be set to True or we get an exception when we try
            # to connect.
            self._smb_con = SMBConnection(username, password, '', 'usersim', is_direct_tcp=True)
            self._smb_con.connect(address, port)
