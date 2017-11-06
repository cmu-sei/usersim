# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import random
import time

import api
from tasks import task


class Frequency(task.Task):
    """ Schedules the nested task an average of frequency times per hour. There is no hard upper limit, but some tasks
    at a high frequency will run the CPU at 100% (generally, ones that interact with external programs).
    """
    def __init__(self, config):
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
        params = {'required': {'task': 'task| the configuration of another task',
                               'frequency': 'number| positive decimal number - avg number of triggers per hour',
                               'repetitions': 'int| non-negative integer - 0 for unlimited'},
                  'optional': {}}

        return params

    @classmethod
    def validate(cls, config):
        """ Check if the given configuration is valid.

        Args:
            config (dict): Configuration dictionary, see parameters method.

        Raises:
            KeyError: If a required key is missing. The error message will be the missing key.
            ValueError: If an argument to an option is invalid. The error message will be as follows:
                key: value reason

        Returns:
            dict: The given configuration dict with arguments converted to their required formats with missing
                optional arguments added with default arguments.
        """
        config = api.check_config(config, cls.parameters(), {})

        freq = config['frequency']
        if freq <= 0:
            raise ValueError('frequency: {} Must be positive.'.format(freq))

        reps = config['repetitions']
        if reps < 0:
            raise ValueError('repetitions: {} Must not be negative.'.format(str(reps)))

        return config
