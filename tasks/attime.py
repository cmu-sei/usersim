# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import datetime

import api
from tasks import task


class AtTime(task.Task):
    """ Schedules the nested task as soon as possible after the specified time passes. If the specified time has already
    passed today, the trigger time will be set at the same time tomorrow instead.
    """
    def __init__(self, config):
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
        required = {'time': 'str| 24-hour time code in HHMM format',
                    'task': 'task| The task to be triggered.'}
        optional = {'seconds': 'number| positive decimal number less than 60 - default is 0',
                    'date': 'str| date stamp in YYYY-MM-DD format - default is today, or tomorrow if time was passed '
                            'today'}

        return {'required': required, 'optional': optional}

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
            dict: The dict given as the config argument with missing optional parameters added with default values.
        """
        defaults = {'seconds': 0.0, 'date': str(datetime.datetime.today().date())}

        config = api.check_config(config, cls.parameters(), defaults)

        time = config['time']
        try:
            datetime.datetime.strptime(time, '%H%M').time()
        except Exception:
            raise ValueError('time: {} Must be in HHMM format'.format(time))

        seconds = config['seconds']
        try:
            assert 0 <= seconds and seconds < 60
        except AssertionError:
            raise ValueError('seconds: {} Must be a number between 0 and 60 non-inclusive'.format(str(seconds)))

        date = config['date']
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d').date()
        except Exception:
            raise ValueError('date: {} Must be in YYYY-MM-DD format'.format(date))

        return config
