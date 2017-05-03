import threading
import traceback


class States(object):
    SCHEDULED, PAUSED, TO_SCHEDULE, TO_PAUSE, TO_STOP, UNKNOWN = range(6)

class UserSim(object):
    # Share one _UserSim object to act like a singleton.
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = _UserSim()
        return cls._instance

class _UserSim(object):
    def __init__(self):
        self._scheduled = dict()
        self._paused = dict()
        # TODO: Should there be a stopped tasks dict to preserve old task IDs, and then a method to clear them manually?

        self._to_schedule = dict()
        self._to_pause = dict()
        self._to_stop = dict()

        self._operation_lock = threading.Lock()

    def loop_cycle(self):
        feedback = list()

        for task_id, task in self._scheduled.items():

            try:
                task()
            except Exception:
                result = traceback.format_exc()
            else:
                result = 'Success'

            # TODO: Needs further consideration.
            feedback.append((task_id, result))

            if task.stop():
                self.stop_task(task_id)

        self._resolve_actions()

        return feedback

    def new_task(self, task, start_paused=False):
        with self._operation_lock:
            if start_paused:
                self._to_pause[id(task)] = task
            else:
                self._to_schedule[id(task)] = task

    def pause_all(self):
        with self._operation_lock:
            for key in list(self._scheduled):
                self._pause_single(key)

    def pause_task(self, task_id):
        with self._operation_lock:
            return self._pause_single(task_id)

    def status_all(self):
        status_list = list()

        with self._operation_lock:
            for key in list(self._scheduled):
                status_list.append(self._status_single(key))

        return status_list

    def status_task(self, task_id):
        with self._operation_lock:
            return self._status_single(task_id)

    def stop_all(self):
        with self._operation_lock:
            for key in list(self._scheduled):
                self._stop_single(key)

    def stop_task(self, task_id):
        with self._operation_lock:
            return self._stop_single(task_id)

    def unpause_all(self):
        with self._operation_lock:
            for key in list(self._scheduled):
                self._unpause_single(key)

    def unpause_task(self, task_id):
        with self._operation_lock:
            return self._unpause_single(task_id)

    def _pause_single(self, task_id):
        if task_id in self._scheduled:
            self._to_pause[task_id] = self._scheduled[task_id]
            return True
        return False

    def _status_single(self, task_id):
        status_dict = dict()

        if task_id in self._scheduled:
            task = self._scheduled[task_id]
            state = States.SCHEDULED
        elif task_id in self._paused:
            task = self._paused[task_id]
            state = States.PAUSED
        elif task_id in self._to_schedule:
            task = self._to_schedule[task_id]
            state = States.TO_SCHEDULE
        elif task_id in self._to_pause:
            task = self._to_pause[task_id]
            state = States.TO_PAUSE
        elif task_id in self._to_stop:
            task = self._to_stop[task_id]
            state = States.TO_STOP
        else:
            task = None
            state = States.UNKNOWN

        if task:
            task_type = task.__module__.split('.')[-1]
        else:
            task_type = 'unknown'

        status_dict['id'] = task_id
        status_dict['state'] = state
        status_dict['type'] = task_type

        return status_dict

    def _stop_single(self, task_id):
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
        if task_id in self._paused:
            self._to_stop[task_id] = self._paused[task_id]
            return True
        return False

    def _resolve_actions(self):
        with self._operation_lock:
            for task_id, task in self._to_pause.items():
                # If these three lines raise, something has gone wrong and we should know about it.
                task_ = self._scheduled.pop(task_id)
                assert task_ is task
                assert task_id not in self._paused
                self._paused[task_id] = task
            self._to_pause = dict()

            for task_id, task in self._to_schedule.items():
                # As above, if the following three lines raise, something is wrong.
                task_ = self._paused.pop(task_id)
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
            # TODO: This should allow the memory to be freed from the stopped tasks, but some tasks could conceivably
            # not fully free their held references from the cleanup method, especially if they use other modules not
            # written in Python. How can I diagnose this before accepting a pull request?
            self._to_stop = dict()
