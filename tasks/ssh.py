from tasks import task

#underscore for private variables

class SSH(task.Task):


	def __init__(self):



	def __call__(self):



	def cleanup(self):
        pass

	def stop(self):
        return True

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











        
