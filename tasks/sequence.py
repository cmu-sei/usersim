# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import api
from tasks import task


class Sequence(task.Task):
    """ Executes nested tasks in sequence. This task is only stopped after the last nested task has stopped.
    """
    def __init__(self, config):
        self._tasks = config['tasks']
        self._waiting = False
        self._index = 0

    def __call__(self):
        if not self._waiting and self._index < len(self._tasks):
            # Start the next task and wait for it.
            self._current = api.new_task(self._tasks[self._index])
            self._waiting = True
            self._index += 1
        if api.status_task(self._current)['state'] == api.States.STOPPED:
            self._waiting = False

    def stop(self):
        if not self._waiting and self._index >= len(self._tasks):
            # Wait until the last task has been stopped before letting this one stop.
            return True
        else:
            return False

    def status(self):
        # Make sure it doesn't change in the middle of creating the string.
        index = self._index

        # Using index as-is here is a shortcut because a user is most likely most familiar with 1-based counting,
        # but still want to give back the correct task type.
        return 'Most recently triggered task {} which has a task type of {}.'.format(index,
                self._tasks[index - 1]['type'])

    def cleanup(self):
        pass

    @classmethod
    def parameters(cls):
        required = {'tasks': '[task]| A list of tasks. Must contain at least two tasks.'}
        optional = {}

        return {'required': required, 'optional': optional}

    @classmethod
    def validate(cls, config):
        config = api.check_config(config, cls.parameters(), {})

        # It doesn't make sense to use this task if there are fewer than two tasks.
        if len(config['tasks']) < 2:
            raise ValueError('tasks: {} Must contain at least two tasks.'.format(config['tasks']))

        return config
