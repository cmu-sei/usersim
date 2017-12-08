# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import queue
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
    PENDING = 'Pending'

class UserSim(object):
    """ Share one _UserSim object to act like a singleton.
    """
    _instance = None

    def __new__(cls, reset=False):
        if cls._instance is None or reset:
            cls._instance = _UserSim()
        return cls._instance

class _UserSim(object):
    """ Manages Task objects internally. No Task should ever reference an object of this class, nor need to.
    """
    def __init__(self):
        self._feedback_queue = queue.Queue()

        self._scheduled = {}
        self._paused = {}

        # Used in order to keep the sanity checks in _resolve_actions.
        self._new = {}

        self._to_schedule = {}
        self._to_pause = {}
        self._to_stop = {}

        # Works around the problems with initializing some tasks from threads that are not the main thread, such as
        # Outlook.
        self._new_tasks_queue = queue.Queue()
        # Works around a bug where adding a task within a cycle, and then immediately checking the status of that task,
        # would return that the task is stopped. Since the task had not yet been actually constructed yet, our below
        # internal ID counter would increment because we returned a task ID, but _status_single would not see the task
        # in any of the dictionaries and report that the task was stopped.
        self._pending = []

        self._operation_lock = threading.Lock()

        # Used to give status about stopped tasks. This variable must not be increased or decreased, only assigned.
        self._current_id = 0
        self._id_gen = self._new_id()

    def cycle(self):
        """ Work through one simulation cycle.

        Returns:
            list of tuples: For each task that ran during this cycle, a tuple of the following is created:
                int: Task ID of the task that ran
                str: A traceback message if an exception occurred, empty string otherwise.
        """
        self._construct_tasks()
        self._resolve_actions()

        for task_id, task in self._scheduled.items():
            try:
                task()
            except Exception:
                self.add_feedback(task_id, traceback.format_exc())

            try:
                stop = task.stop()
            except Exception:
                stop = True
                self.add_feedback(task_id, 'Exception on calling stop method:\n\n' + traceback.format_exc())

            if stop:
                # Get its status before it's actually stopped because stopping removes the task from memory.
                # Manually set the state to stopped because the final status will still say the task is scheduled.
                final_status = self.status_task(task_id)
                final_status['state'] = States.STOPPED
                self._add_feedback(final_status, '')

                self.stop_task(task_id)

        feedback = []
        while not self._feedback_queue.empty():
            feedback.append(self._feedback_queue.get())
        return feedback

    def new_task(self, task_class, task_config, start_paused=False):
        """ Manage a task. Guaranteed thread-safe.

        Arguments:
            task (class): The CLASS of the task to construct.
            config (dict): A pre-validated task config.
            start_paused (bool): Whether the given task will start scheduled (True) or paused (False).

        Returns:
            int: A value uniquely associated with the given task.
        """
        with self._operation_lock:
            task_id = next(self._id_gen)
            self._current_id = task_id
            self._pending.append(task_id)

            self._new_tasks_queue.put((task_id, task_class, task_config, start_paused))

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
        status_list = []

        with self._operation_lock:
            for key in self._scheduled:
                status_list.append(self._status_single(key))
            for key in self._paused:
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

    def add_feedback(self, task_id, error):
        """ Add a feedback message for the next cycle. Guaranteed thread-safe.

        Args:
            task_id (int): A task ID to associate the feedback with.
            error (str): An error string giving either a traceback (traceback.format_exc() is preferred) or a
                human-readable explanation of the error condition.
        """
        try:
            status = self.status_task(task_id)
        except AssertionError:
            # Someone likely called this with a bad task ID.
            return

        if not isinstance(error, str):
            # Pretty much guaranteed to convert to a string, but what it actually creates may not be intended.
            error = str(error)
        self._add_feedback(status, error)

    def _add_feedback(self, status_dict, error):
        self._feedback_queue.put((status_dict, error))

    def _new_task(self, task_id, task_class, task_config, start_paused):
        """ Do task construction and add the constructed task to internal structures. NOT thread-safe, and should only
        be called from the main thread due to the fragility of some of the interactions with external programs in some
        tasks.

        Arguments:
            task_id (int): The new task's internal ID.
            task_class (class): The CLASS of the new task to be constructed.
            task_config (dict): A pre-validated task config.
            start_paused (bool): Whether the given task will start scheduled (True) or paused (False).

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        task = task_class(task_config)
        task._task_id = task_id

        if start_paused:
            self._to_pause[task_id] = task
        else:
            self._to_schedule[task_id] = task

        self._new[task_id] = task

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
            task_id (int > 0): The value returned by the new_task method when the task to be paused was added.

        Returns:
            dict: A dictionary with the following key:value pairs:
                'id':int
                'type':str
                'state':str
                'status':str
        """
        assert task_id > 0

        status_dict = {}

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
        elif task_id in self._pending:
            # Not ready yet, so we don't have any further information about the task.
            task = None
            state = States.PENDING
        elif task_id <= self._current_id:
            task = None
            state = States.STOPPED
        else:
            task = None
            state = States.UNKNOWN

        if task:
            task_type = self._get_task_type(task)
            try:
                status = task.status()
            except Exception as e:
                status = 'Exception while checking status:\n\n' + str(e)
        elif state == States.STOPPED:
            task_type = 'unknown'
            status = 'dead'
        elif state == States.PENDING:
            task_type = 'unknown'
            status = 'pending'
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
            self._to_schedule[task_id] = self._paused[task_id]
            return True
        return False

    def _construct_tasks(self):
        """ Handle task initialization while catching exceptions.
        """
        with self._operation_lock:
            self._pending = []
            while not self._new_tasks_queue.empty():
                # Here we do new task construction within the main thread.
                task_id, task_class, task_config, start_paused = self._new_tasks_queue.get()
                try:
                    self._new_task(task_id, task_class, task_config, start_paused)
                except Exception:
                    status_dict = {'id': task_id,
                                   'state': States.STOPPED,
                                   'type': self._get_task_type(task_class),
                                   'status': 'Failed to initialize task.'}
                    self._feedback_queue.put((status_dict, traceback.format_exc()))

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
            self._to_pause = {}

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
            self._to_schedule = {}

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
                try:
                    task.cleanup()
                except Exception:
                    status = self._status_single(task_id)
                    self._add_feedback(status, 'Exception while calling task cleanup:\n\n' + traceback.format_exc())

            self._to_stop = {}

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

