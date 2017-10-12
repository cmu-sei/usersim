import random
import time

import api
from tasks import task


class Frequency(task.Task):
    """ Schedules the nested task an average of frequency times per hour. There is no hard upper limit, but some tasks
    at a high frequency will run the CPU at 100% (generally, ones that interact with external programs).
    """
    def __init__(self, config):
        config = self.validate(config)
        freq = config['frequency']
        reps = config['repetitions']
        task = config['task']

        self._time_per_trigger = 3600 / freq
        self._reps = reps
        self._triggered = 0
        self._task = task
        self._last_check = time.time()

    def __call__(self):
        now = time.time()
        slept = now - self._last_check
        self._last_check = now

        trigger_probability = slept / self._time_per_trigger
        if random.random() < trigger_probability:
            self._triggered += 1
            api.new_task(self._task)

    def cleanup(self):
        pass

    def stop(self):
        if self._reps == 0 or self._triggered < self._reps:
            return False
        else:
            return True

    def status(self):
        return 'Triggered %d times.' % self._triggered

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with human-readable descriptions of required arguments for the Frequency task.

        Returns:
            dict of dicts: Configuration dictionary with the keys 'required' and 'optional', where values are dicts
                containing the required and optional parameters and their descriptions for the Frequency task,
                respectively.
        """
        params = {'required': {'task': 'the configuration of another task',
                               'frequency': 'positive decimal number - avg number of triggers per hour',
                               'repetitions': 'non-negative integer - 0 for unlimited'},
                  'optional': {}}

        return params

    @classmethod
    def validate(cls, config):
        """ Check if the given configuration is valid.

        Args:
            config (dict): Configuration dictionary with the following keys:
                frequency (float > 0): Average number of occurences per hour.
                repetitions (int >= 0): Maximum number of times to trigger. 0 indicates no maximum.
                task (dict): Configuration for a nested task.

        Raises:
            KeyError: If a required key is missing. The error message will be the missing key.
            ValueError: If an argument to an option is invalid. The error message will be as follows:
                key: value reason

        Returns:
            dict: The given configuration dict with arguments converted to their required formats with missing
                optional arguments added with default arguments.
        """
        converted = dict()

        if 'frequency' not in config:
            raise KeyError('frequency')
        else:
            freq = config['frequency']
            try:
                freq = float(freq)
            except ValueError:
                raise ValueError('frequency: {} Not a valid number.'.format(str(freq)))
            if freq <= 0:
                raise ValueError('frequency: {} Must be non-negative.'.format(str(freq)))

        if 'repetitions' not in config:
            raise KeyError('repetitions')
        else:
            reps = config['repetitions']
            try:
                reps = int(reps)
            except ValueError:
                raise ValueError('repetitions: {} Not a valid number'.format(str(reps)))
            if reps < 0:
                raise ValueError('repetitions: {} Must be positive'.format(str(reps)))

        if 'task' not in config:
            raise KeyError(param_missing % 'task')
        else:
            task = config['task']
            if not isinstance(task, dict):
                raise ValueError('task: {} Must be a dictionary.'.format(str(task)))
            api.validate_config(task)

        converted['frequency'] = freq
        converted['repetitions'] = reps
        converted['task'] = task

        return converted
