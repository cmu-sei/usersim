import telnetlib
import time

from tasks import task


class Telnet(task.Task):
    """ Connect to the configured machine and send it a list of commands via Telnet.
    """
    def __init__(self, config):
        self._config = config

    def __call__(self):
        self.telnet_to(self._config['host'],
                       self._config['port'],
                       self._config['username'],
                       self._config['password'],
                       self._config['commandlist'])

    def cleanup(self):
        """
        Doesn't do anything
        """
        pass

    def stop(self):
        """
        Task should stop after it is run once
        """
        return True

    def status(self):
        return ''

    def telnet_to(self, hostname, port, username, password, commandlist):
        telnetclient = telnetlib.Telnet(hostname, port, 10)

        # telnetclient.write expects byte input so we have to encode it.
        telnetclient.write((username + '\n').encode('ascii'))
        if password:
            telnetclient.write((password + '\n').encode('ascii'))
            time.sleep(4)
        for command in commandlist:
            telnetclient.write((command + '\n').encode('ascii'))
            time.sleep(1)
            print(telnetclient.read_very_eager())
        time.sleep(2)
        telnetclient.write(('exit\n').encode('ascii'))
        telnetclient.close()

    @classmethod
    def parameters(cls):
        parameters = {'required': {'host': 'str| host to connect to',
                                   'username': 'str| username to connect with',
                                   'password': 'str| password to connect with',
                                   'commandlist': '[str]| commands to send'},
                      'optional': {'port': 'int| port to connect on, default 23'}}

        return parameters

    @classmethod
    def validate(cls, conf_dict):
        parameters = cls.parameters()
        required = parameters['required']
        optional = parameters['optional']

        for item in required:
            if item not in conf_dict:
                raise KeyError(item)

        for item in ['host', 'username', 'password']:
            if not isinstance(conf_dict[item], str):
                raise ValueError(item + ': {} Must be string'.format(str(conf_dict[item])))

        if not isinstance(conf_dict['commandlist'], list):
            raise ValueError('commandlist: {} Must be list of strings'.format(str(conf_dict['commandlist'])))
        for item in conf_dict['commandlist']:
            if not isinstance(item, str):
                raise ValueError('commandlist: {} Must be list of strings'.format(str(conf_dict['commandlist'])))

        if 'port' not in conf_dict:
            conf_dict['port'] = 23
        elif not isinstance(conf_dict['port'], int):
            raise ValueError('port: {} Must be an int.'.format(str(conf_dict['port'])))

        return conf_dict
