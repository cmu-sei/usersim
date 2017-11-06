# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import api
from tasks import sequence


class All(sequence.Sequence):
    """ Runs all tasks given by its configuration. This task is only stopped once all of its nested tasks have
    stopped. Mainly used for nesting multiple tasks within another task.
    """
    def __init__(self, config):
        self._tasks = config['tasks']
        self._task_ids = set()
        self._stopped_task_ids = set()
        self._done = False
        self._started = False

    def __call__(self):
        if not self._started:
            for task in self._tasks:
                task_id = api.new_task(task)
                self._task_ids.add(task_id)
            self._started = True


        self._stopped_task_ids = set()
        for task_id in self._task_ids:
            # Check that all nested tasks have stopped.
            if api.status_task(task_id)['state'] == api.States.STOPPED:
                # Would do self._task_ids.remove here, but we can't modify the data structure while iterating over it.
                self._stopped_task_ids.add(task_id)
            else:
                break
        else:
            # Since they are uncommon, the else part of a for-else executes when the for loop completes without a break.
            self._done = True

        # No point repeating work that's already been completed.
        self._task_ids = self._task_ids - self._stopped_task_ids

    def stop(self):
        return self._done

    def status(self):
        return 'Tasks with IDs {} have finished.'.format(self._stopped_task_ids)
