from tasks import task

class SSH(task.Task):
    def __init__(self, config):
        """ Validates config and stores it as an attribute

        Returns None
        """
        self._config = self.validate(config)

    def __call__(self):
        """ Connects to the SSH server specified in config.

        Returns None
        """
        self.ssh_to(self._config['host'],
                    self._config['user'],
                    self._config['passwd'],
                    self._config['cmdlist'],
                    self._config['policy'],
                    self._config['port'])

    def cleanup(self):
        """ Doesn't do anything

        Returns None
        """
        pass

    def stop(self):
        """ Task should stop after it is run once

        Returns True
        """
        return True

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        raise NotImplementedError("Not yet implemented.")

	@classmethod
	def parameters(cls):
        params = {"required": 
                    {"host": 'str: the hostname to connect to, ex. "io.smashthestack.org"', 
                    "user": 'str: username to login with, ex. "level1"', 
                    "passwd": 'str: password to login with, ex. "level1"', 
                    "cmdlist": 'list: strs to send as commands, ex. ["ls -la", "cat README"]', 
                    },
                "optional": 
                {
                    "port": 'int or str: of the port on which to connect to the SSH server, ex. 22 or "22".  Default: 22'
                    "policy": 'str: which policy to adopt in regards to missing host keys, should be one of "AutoAdd", "Reject", or "Warning". Default: Warning'}
                }
        return params

	@classmethod
	def validate(cls, conf_dict):
        super().validate(conf_dict)

        #more detailed task-specific commands can go here
        policy_opts = ['AutoAdd', 'Reject', 'Warning']
        if conf_dict["policy"] not in policy_opts:
            raise ValueError("policy: " + conf_dict["policy"].value)

        return conf_dict

    def ssh_to(self, host, user, passwd, cmdlist, policy, port = 22):
        """
        Connects to an SSH server at host:port with user as the username and passwd as the password.
        Proceeds to execute all commands in cmdlist.
        Returns None
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