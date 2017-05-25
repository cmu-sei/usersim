import threading
import traceback


class States(object):
    SCHEDULED = 'Scheduled'
    PAUSED = 'Paused'
    STOPPED = 'Stopped'
    NEW = 'New'
    TO_SCHEDULE = 'Scheduling'
    TO_PAUSE = 'Paused'
    TO_STOP = 'Stopping'
    UNKNOWN = 'Unknown'

class UserSim(object):
    """ Share one _UserSim object to act like a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = _UserSim()
        return cls._instance

class _UserSim(object):
    """ Manages Task objects internally. No Task should ever reference an object of this class, nor need to.
    """
    def __init__(self):
        self._scheduled = dict()
        self._paused = dict()
        # TODO: If we keep track of dead tasks, that means that the simulator WILL eventually run out of memory.
        # It's nice keeping track of the types of dead tasks, but this must be handled in a better way. Maybe clean
        # this dict out periodically, or just use the current highest ID to determine if a task is stopped.
        self._stopped = dict()

        # Used in order to keep the sanity checks in _resolve_actions.
        self._new = dict()

        self._to_schedule = dict()
        self._to_pause = dict()
        self._to_stop = dict()

        self._operation_lock = threading.Lock()

        self._id_gen = self._new_id()

    def cycle(self):
        """ Work through one simulation cycle.
        """
        feedback = list()

        for task_id, task in self._scheduled.items():

            try:
                # TODO: This should have a watchdog timer - unsure if individual tasks should set their own timers or
                # if the timer should be a guaranteed global.
                task()
            except Exception:
                result = 'Failure'
                exception = traceback.format_exc()
            else:
                result = 'Success'
                exception = None

            # TODO: This should probably construct a feedback message object - NYI.
            feedback.append((task_id, result, exception))

            if task.stop():
                self.stop_task(task_id)

        self._resolve_actions()

        return feedback

    def new_task(self, task, start_paused=False):
        """ Manage a task.

        Arguments:
            task (tasks.task.Task): A constructed Task object that is ready to run.
            start_paused (bool): Whether the given task will start scheduled (True) or paused (False).

        Returns:
            int: A value uniquely associated with the given task.
        """
        with self._operation_lock:
            task_id = next(self._id_gen)
            if start_paused:
                self._to_pause[task_id] = task
            else:
                self._to_schedule[task_id] = task

            self._new[task_id] = task

        return task_id

    def pause_all(self):
        """ Pause all tasks that are currently scheduled. Guaranteed thread-safe.
        """
        with self._operation_lock:
            for key in self._scheduled:
                self._pause_single(key)

    def pause_task(self, task_id):
        """ Pause an individual task. Guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        with self._operation_lock:
            return self._pause_single(task_id)

    def status_all(self):
        """ Get a list of the status of all managed tasks. Guaranteed thread-safe.

        Returns:
            list of dicts: Each dictionary will have the following key:value pairs:
                'id':int
                'type':str
                'state':str
                'status':str
        """
        status_list = list()

        with self._operation_lock:
            for key in self._scheduled:
                status_list.append(self._status_single(key))
            for key in self._paused:
                status_list.append(self._status_single(key))
            for key in self._stopped:
                status_list.append(self._status_single(key))
            for key in self._new:
                status_list.append(self._status_single(key))

        return status_list

    def status_task(self, task_id):
        """ Return the status of a particular task. Guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            dict: A dictionary with the following key:value pairs:
                'id':int
                'type':str
                'state':str
                'status':str
        """
        with self._operation_lock:
            return self._status_single(task_id)

    def stop_all(self):
        """ Stop all tasks that are currently scheduled or paused. Guaranteed thread-safe.
        """
        with self._operation_lock:
            for key in self._scheduled:
                self._stop_single(key)
            for key in self._paused:
                self._stop_single(key)

    def stop_task(self, task_id):
        """ Stop a particular task. Guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        with self._operation_lock:
            return self._stop_single(task_id)

    def unpause_all(self):
        """ Unpause all tasks that are currently paused. Guaranteed thread-safe.
        """
        with self._operation_lock:
            for key in self._paused:
                self._unpause_single(key)

    def unpause_task(self, task_id):
        """ Unpause a particular task. Guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        with self._operation_lock:
            return self._unpause_single(task_id)

    def _pause_single(self, task_id):
        """ Pause an individual task. NOT guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if task_id in self._scheduled:
            self._to_pause[task_id] = self._scheduled[task_id]
            return True
        return False

    def _status_single(self, task_id):
        """ Return the status of a particular task. NOT guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            dict: A dictionary with the following key:value pairs:
                'id':int
                'type':str
                'state':str
                'status':str
        """
        status_dict = dict()

        if task_id in self._to_schedule:
            task = self._to_schedule[task_id]
            state = States.TO_SCHEDULE
        elif task_id in self._to_pause:
            task = self._to_pause[task_id]
            state = States.TO_PAUSE
        elif task_id in self._to_stop:
            task = self._to_stop[task_id]
            state = States.TO_STOP
        elif task_id in self._scheduled:
            task = self._scheduled[task_id]
            state = States.SCHEDULED
        elif task_id in self._paused:
            task = self._paused[task_id]
            state = States.PAUSED
        elif task_id in self._stopped:
            # Stopped task references have been dropped.
            task = None
            state = States.STOPPED
        elif task_id in self._new:
            # Actually, new tasks will always be in _to_pause or _to_schedule, so we should never get this status.
            # It's fine to leave it for now.
            task = self._new[task_id]
            state = States.NEW
        else:
            task = None
            state = States.UNKNOWN

        if task:
            task_type = self._get_task_type(task)
            status = task.status()
        elif state == States.STOPPED:
            task_type = self._stopped[task_id]
            status = 'dead'
        else:
            task_type = 'unknown'
            status = 'unknown'

        status_dict['id'] = task_id
        status_dict['state'] = state
        status_dict['type'] = task_type
        status_dict['status'] = status

        return status_dict

    def _stop_single(self, task_id):
        """ Stop a particular task. NOT guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if task_id in self._scheduled:
            self._to_stop[task_id] = self._scheduled[task_id]
        elif task_id in self._paused:
            self._to_stop[task_id] = self._paused[task_id]
        elif task_id in self._to_schedule:
            self._to_stop[task_id] = self._to_schedule[task_id]
        elif task_id in self._to_pause:
            self._to_stop[task_id] = self._to_pause[task_id]
        else:
            # The task was either already stopped at the end of the last cycle, or it doesn't exist at all.
            return False
        return True

    def _unpause_single(self, task_id):
        """ Unpause a particular task. NOT guaranteed thread-safe.

        Arguments:
            task_id (int): The value returned by the new_task method when the task to be paused was added.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        if task_id in self._paused:
            self._to_stop[task_id] = self._paused[task_id]
            return True
        return False

    def _resolve_actions(self):
        """ Handle all changes in scheduling. Guaranteed thread-safe.
        """
        # Definitely want to lock to prevent any changes to these structures while resolving.
        with self._operation_lock:
            for task_id, task in self._to_pause.items():
                # If these three lines raise, something has gone wrong and we should know about it.
                try:
                    task_ = self._scheduled.pop(task_id)
                except KeyError:
                    # When a task is new, it will be in _to_pause without having ever been in _scheduled.
                    task_ = self._new.pop(task_id)
                assert task_ is task
                assert task_id not in self._paused
                self._paused[task_id] = task
            self._to_pause = dict()

            for task_id, task in self._to_schedule.items():
                # As above, if the following three lines raise, something is wrong.
                try:
                    task_ = self._paused.pop(task_id)
                except KeyError:
                    # When a task is new, it will be in _to_schedule without having ever been in _paused.
                    task_ = self._new.pop(task_id)
                assert task_ is task
                assert task_id not in self._scheduled
                self._scheduled[task_id] = task
            self._to_schedule = dict()

            for task_id, task in self._to_stop.items():
                task_ = self._scheduled.pop(task_id, None)
                if task_ is None:
                    task_ = self._paused.pop(task_id, None)
                if task_ is None:
                    task_ = self._to_schedule.pop(task_id, None)
                if task_ is None:
                    task_ = self._to_pause.pop(task_id, None)

                # If this raises, how did this happen?
                assert task_ is task
                task.cleanup()

                # Still keep tracking the ID and task type so we can report the task's stopped status.
                self._stopped[task_id] = self._get_task_type(task)

            self._to_stop = dict()

    @staticmethod
    def _new_id():
        current_id = 0
        while True:
            current_id += 1
            yield current_id

    @staticmethod
    def _get_task_type(task):
        """ Return the type of the given task.
        """
        return task.__module__.split('.')[-1]

