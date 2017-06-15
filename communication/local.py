import threading
import time

import api
import config


class LocalCommunication(object):
    def __init__(self, feedback_queue, file_name):
        self._feedback_queue = feedback_queue

        with open(file_name, 'r') as f:
            config_string = f.read()

        new_config = config.string_to_python(config_string)
        for task in new_config:
            try:
                api.new_task(task)
            except KeyError as e:
                self._feedback_queue.put((0, 'task ' + task['type'] + 'missing required key %s '
                    'from its configuration' % e.message))
            except ValueError as e:
                self._feedback_queue.put((0, 'task ' + task['type'] + 'has at least one bad value for a config '
                    'option:\n%s' % e.message))

        thread = threading.Thread(target=self._handle_communication)
        thread.daemon = True
        thread.start()

    def _send(self):
        """ Write available feedback messages to the console.
        """
        print('\n' * 3)
        while not self._feedback_queue.empty():
            task_id, exception = self._feedback_queue.get()

            if task_id > 0:
                task_status = api.status_task(task_id)
            else:
                task_status = {'type': 'core', 'state': api.States.UNKNOWN, 'status': str()}

            if exception:
                print('The following task FAILED an iteration:')
            else:
                print('The following task WAS SCHEDULED TO STOP:')
            print('Type: ' + task_status['type'])
            print('ID: ' + task_id)
            print('State: ' + task_status['state'])
            print('Status: ' + task_status['status'])
            if exception:
                print('Exception: \n' + exception)
            print('=' * 40)

        print('\n' * 3)
        print('=' * 40)

    def _handle_communication(self):
        """ Periodically write feedback messages to the console.
        """
        self._send()
        time.sleep(60)
