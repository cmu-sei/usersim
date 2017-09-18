import datetime

import api
from tasks import task


class AtTime(task.Task):
    def __init__(self, config):
        config = self.validate(config)
        time = datetime.datetime.strptime(config['time'], '%H%M').time()
        seconds = datetime.timedelta(seconds=config['seconds'])
        date = datetime.datetime.strptime(config['date'], '%Y-%m-%d').date()
        task = config['task']

        trigger_time = datetime.datetime.combine(date, time) + seconds

        if datetime.datetime.now() > trigger_time:
            # If the trigger time has passed for today, just trigger it tomorrow at that time.
            trigger_time += datetime.timedelta(days=1)
        self._trigger_time = trigger_time
        self._task = task
        self._triggered = False

    def __call__(self):
        if datetime.datetime.now() >= self._trigger_time:
            self._triggered = True
            api.new_task(self._task)

    def cleanup(self):
        pass

    def stop(self):
        return self._triggered

    def status(self):
        if self._triggered:
            return 'Nested task has triggered.'
        else:
            return 'Nested task will trigger at %s' % str(self._trigger_time)

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        required = {'time': 'str: 24-hour time code in HHMM format',
                    'task': 'task: The task to be triggered.'}
        optional = {'seconds': 'float: positive decimal number less than 60 - default is 0',
                    'date': 'str: date stamp in YYYY-MM-DD format - default is today, or tomorrow if time was passed '
                            'today'}

        return {'required': required, 'optional': optional}

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
                'time':str - HHMM formatted timestamp
                'seconds':float - 0 <= number < 60, default 0
                'date':str - YYYY-MM-DD formatted date, default today
        """
        for key in cls.parameters()['required']:
            if key not in conf_dict:
                raise KeyError(key)

        time = conf_dict['time']
        try:
            datetime.datetime.strptime(str(time), '%H%M').time()
        except Exception:
            raise ValueError('time: {} Must be in HHMM format'.format(str(time)))

        seconds = conf_dict.get('seconds', 0.0)
        try:
            seconds = float(seconds)
            assert 0 <= seconds and seconds < 60
        except Exception:
            raise ValueError('seconds: {} Must be a number between 0 and 60 non-inclusive'.format(str(seconds)))

        date = conf_dict.get('date', str(datetime.datetime.today().date()))
        try:
            datetime.datetime.strptime(str(date), '%Y-%m-%d').date()
        except Exception:
            raise ValueError('date: {} Must be in YYYY-MM-DD format'.format(str(date)))

        task = conf_dict['task']
        api.validate_config(task)

        return {'time': time, 'seconds': seconds, 'date': date, 'task': task}
