import datetime

import api
from tasks import attime


class Delay(attime.AtTime):
    """ Schedules the nested task as soon as possible after the specified delay has elapsed.
    """
    def __init__(self, config):
        days = config['days']
        hours = config['hours']
        minutes = config['minutes']
        seconds = config['seconds']
        task = config['task']

        delay_time = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

        self._trigger_time = datetime.datetime.now() + delay_time
        self._task = task
        self._triggered = False

    @classmethod
    def parameters(cls):
        required = {'task': 'task| The task to be triggered'}
        optional = {'days': 'int| Number of days to delay the nested task. Must not be negative. Default 0.',
                    'hours': 'int| Number of hours to delay the nested task. Must not be negative. Default 0.',
                    'minutes': 'int| Number of minutes to delay the nested task. Must not be negative. Default 0.',
                    'seconds': 'int| Number of seconds to delay the nested task. Must not be negative. Default 0.'}
        return {'required': required, 'optional': optional}

    @classmethod
    def validate(cls, config):
        defaults = {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0}
        parameters = cls.parameters()
        optional = parameters['optional']

        config = api.check_config(config, parameters, defaults)

        for key in optional:
            value = config[key]
            if value < 0:
                raise ValueError('{}: {} Must not be negative'.format(key, value))

        return config
