import paramiko

from task import task

MAX_RECV = 4096
BLOCKING = True

class SSH(task.Task):
    def __init__(self, config):
        self._config = self.validate(config)

    def __call__(self):
        """ Periodically called while the object is scheduled. This gives the object its behavior, whatever that may
        entail.

        Returns:
            dict or None: If this task wants another task to be scheduled, this call should return the
                configuration for that task as a dict. Otherwise, it should not return anything, which is equivalent
                to returning None.
        """
        self.ssh_to(self._config['host'],
                    self._config['user'],
                    self._config['passwd'],
                    self._config['cmdlist'],
                    self._config['policy'],
                    self._config['port'])

    def cleanup(self):
        """ Called in the event __call__ raises an exception or when the stop method returns True. This method should
        never raise an exception. Use this method to handle cleaning up any open handles, files, or whatever needs to be
        closed in order to free up the memory that this object is using. This method must be overridden, but it is fine
        for it not to actually do anything if that is intended functionality.
        """
        pass

    def stop(self):
        """ Each time the task runs, the scheduler subsequently calls this method to check if the Task object
        should be descheduled.

        Returns:
            bool: True if this object should be descheduled. False if it should stay in the scheduler.
        """
        raise NotImplementedError("Not yet implemented.")

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        raise NotImplementedError("Not yet implemented.")

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {'required': {'host': 'str of the hostname to connect to, ex. "io.smashthestack.org"',
                               'user': 'str of username to log in with, ex. "user1"',
                               'passwd': 'str of password to log in with, ex. "p@ssw0rd1"',
                               'cmdlist': 'list of strs to send as commands, ex. ["ls -la", "cat README"]',
                               'policty': 'str of which policy to adopt with regards to missing host keys; should be one of "AutoAdd", "Reject", or "Warning"'},
                  'optional': {'port': 'int or str of the port on which to connect to the SSH server, ex 22 or "22"; defaults to "22"'}}
        return params

    @classmethod
    def validate(cls, conf_dict):
        """ Validates the given configuration dictionary.

        Args:
            conf_dict (dict): The dictionary to validate. Its keys and values are subclass-specific.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the conf_dict argument with missing optional parameters added with default values.
        """
        raise NotImplementedError("Not yet implemented.")

    def ssh_to(self, host, user, passwd, cmdlist, policy, port = 22):
        """
        Connects to an SSH server at host:port with user as the username and passwd as the password.
        Proceeds to execute all commands in cmdlist.
        """
        ssh = paramiko.SSHClient()
        if policy == "AutoAdd":
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        elif policy == "Reject":
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        elif policy == "Warning":
            ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        ssh.connect(host, int(port),user, passwd)
        channel = ssh.invoke_shell()
        channel.setblocking(int(BLOCKING))
        channel.sendall("")
        incoming = ""

        #Receive the welcome message from the server and print it.  If any of this fails,
        #something went wrong with the connection.
        while channel.recv_ready():
            incoming += channel.recv(MAX_RECV)
            time.sleep(.1)
        sys.stdout.write(incoming)

        for command in cmdlist:
            channel.sendall(command + "\n")
            time.sleep(.5)
            incoming = ""
            while channel.recv_ready():
                incoming += channel.recv(MAX_RECV)
                time.sleep(.1)
            sys.stdout.write(incoming)

        try: # Try to close the connection, but we don't want to raise an exception here if it fails
            ssh.close()
        except:
            pass
        print("") # So that the next output will be on a new line
