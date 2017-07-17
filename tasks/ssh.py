# Ali Kidwai
# June 16, 2017
# Adapted from code written by Rotem Guttman and Joe Vessella

import sys
import time

import paramiko

from tasks import task


MAX_RECV = 4096
BLOCKING = True

class SSH(task.Task):
    """ SSH module for UserSim. Connects to and authenticates with a host, then sends a sequence of shell commands.
    """
    def __init__(self, config):
        """ Validates config and stores it as an attribute
        """
        self._config = self.validate(config)

    def __call__(self):
        """ Connects to the SSH server specified in config.
        """
        self.ssh_to(self._config['host'],
                    self._config['user'],
                    self._config['password'],
                    self._config['cmdlist'],
                    self._config['policy'],
                    self._config['port'])

    def cleanup(self):
        """ Doesn't need to do anything
        """
        return None

    def stop(self):
        """ Task should stop after it is run once

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

    def ssh_to(self, host, user, password, cmdlist, policy, port):
        """ Connects to an SSH server at host:port with user as the username and password as the password. Proceeds to
        execute all commands in cmdlist.
        """
        ssh = paramiko.SSHClient()
        if policy == "AutoAdd":
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        elif policy == "Reject":
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        elif policy == "Warning":
            ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        ssh.connect(host, port, user, password)
        channel = ssh.invoke_shell()
        channel.setblocking(int(BLOCKING))
        channel.sendall("")
        incoming = ""

        # Receive the welcome message from the server and print it.  If any of this fails, something went wrong with
        # the connection.
        while channel.recv_ready():
            incoming += channel.recv(MAX_RECV).decode()
            time.sleep(.1)
        sys.stdout.write(incoming)
        sys.stdout.flush()

        for command in cmdlist:
            channel.sendall(command + "\n")
            time.sleep(.5)
            incoming = ""
            while channel.recv_ready():
                incoming += channel.recv(MAX_RECV).decode()
                time.sleep(.1)
            sys.stdout.write(incoming)
            sys.stdout.flush()

        try: # Try to close the connection, but we don't want to raise an exception here if it fails
            ssh.close()
        except:
            pass
        print("") # So that the next output will be on a new line

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {"required": {"host": 'the hostname to connect to, ex. "io.smashthestack.org"',
                               "user": 'username to login with, ex. "level1"',
                               "password": 'password to login with, ex. "level1"',
                               "cmdlist": 'list of strings to send as commands, ex. ["ls -la", "cat README"]'},
                  "optional": {"port": 'the port on which to connect to the SSH server, ex. 22.  Default: 22',
                               "policy": 'which policy to adopt in regards to missing host keys, should be one of '
                                         'AutoAdd, Reject, or Warning. Default: Warning'}}
        return params

    @classmethod
    def validate(cls, config):
        """ Validates the given configuration dictionary.

        Args:
            config (dict): The dictionary to validate. Its keys and values are subclass-specific.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the conf_dict argument with missing optional parameters added with default values.
        """
        params = cls.parameters()
        reqd_params = params['required']
        for key in reqd_params:
            if key not in config:
                raise KeyError(key)

        for key in ["host", "user", "password"]:
            if type(config[key]) != str:
                raise ValueError(key + ": {} Must be a string".format(str(config[key])))
        if not config["host"]:
            raise ValueError("host: {} Must be non-empty".format(str(config["host"])))
        if type(config["cmdlist"]) != list:
            raise ValueError("cmdlist: {} Must be a list of strings".format(str(config["cmdlist"])))
        if not config["cmdlist"]:
            raise ValueError("cmdlist: {} Must be non-empty".format(str(config["host"])))
        for command in config["cmdlist"]:
            if type(command) != str:
                raise ValueError("cmdlist: {} Must be a list of strings".format(str(config["cmdlist"])))

        if "policy" not in config:
            config["policy"] = "Warning"
        if "port" not in config:
            config["port"] = 22
        if config["policy"] not in ["AutoAdd", "Reject", "Warning"]:
            raise ValueError("policy: {} Must be one of 'AutoAdd', 'Reject', "
                             "or 'Warning'".format(str(config["policy"])))
        if type(config["port"]) != int:
            raise ValueError("port: {} Must be an int".format(str(config["port"])))
        if config["port"] < 1 or config["port"] > 65536:
            raise ValueError("port: {} Must be in the range [1, 65536]".format(str(config["port"])))

        return config
