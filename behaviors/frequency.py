import random
import time

from behaviors import behavior


class Frequency(behavior.Behavior):
    def __init__(self, freq, reps, behavior):
        """
        Args:
            freq (float > 0): Average number of occurences per hour.
            reps (int >= 0): Maximum number of times to trigger. 0 imposes no limit.
        """
        self._time_per_trigger = 3600 / freq
        self._reps = reps
        self._triggered = 0
        self._behavior = behavior
        self._last_check = time.time()

    def __call__(self):
        now = time.time()
        slept = now - self._last_check
        self._last_check = now

        trigger_probability = slept / self._time_per_trigger
        if random.random() < trigger_probability:
            self._triggered += 1
            return self._behavior

    def cleanup(self):
        pass

    def stop(self):
        if self._reps == 0 or self._triggered < self._reps:
            return False
        else:
            return True

    @classmethod
    def config(cls, conf_dict):
        """ Configures a Frequency object.

        Args:
            conf_dict (dict): Configuration dictionary with the following keys:
                frequency (float > 0): Average number of occurences per hour.
                repetitions (int >= 0): Maximum number of times to trigger. 0 indicates no maximum.
                behavior (dict): Configuration for a nested behavior.

        Returns:
            Frequency: A constructed Frequency object.
        """
        param_missing = '%s parameter missing from configuration'
        not_a_number = 'Given %s value %s cannot be interpreted as a number.'
        invalid_input = 'Given %s value %s, which is not valid.'

        if 'frequency' not in conf_dict:
            raise KeyError(param_missing % 'frequency')
        else:
            freq = conf_dict['frequency']
            try:
                freq = float(freq)
            except ValueError:
                raise ValueError(not_a_number % ('frequency', str(freq)))
            if freq <= 0:
                raise ValueError(invalid_input % ('frequency', '%s <= 0' % str(freq)))

        if 'repetitions' not in conf_dict:
            raise KeyError(param_missing % 'repetitions')
        else:
            reps = conf_dict['repetitions']
            try:
                reps = int(reps)
            except ValueError:
                raise ValueError(not_a_number % ('repetitions', str(reps)))
            if reps < 0:
                raise ValueError(invalid_input % ('repetitions', '%s <= 0' % str(reps)))

        if 'behavior' not in conf_dict:
            raise KeyError(param_missing % 'behavior')
        else:
            behavior = conf_dict['behavior']

        return cls(freq, reps, behavior)

type_dict = {'frequency': Frequency}
