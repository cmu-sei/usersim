import textwrap
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
                task_status = {'id': 0, 'type': 'core', 'state': api.States.UNKNOWN, 'status': str()}
                self._feedback_queue.put((task_status, 'task ' + task['type'] + 'missing required key %s '
                    'from its configuration' % e.message))
            except ValueError as e:
                task_status = {'id': 0, 'type': 'core', 'state': api.States.UNKNOWN, 'status': str()}
                self._feedback_queue.put((task_status, 'task ' + task['type'] + 'has at least one bad value for a '
                    'config option:\n%s' % e.message))

        thread = threading.Thread(target=self._handle_communication)
        thread.daemon = True
        thread.start()

    def _send(self):
        """ Write available feedback messages to the console.
        """
        while not self._feedback_queue.empty():
            print('=' * 40)
            task_status, exception = self._feedback_queue.get()

            if exception:
                print('The following task FAILED an iteration:')
            else:
                print('The following task WAS SCHEDULED TO STOP:')
            print('Type: ' + task_status['type'])
            print('ID: ' + str(task_status['id']))
            print('State: ' + task_status['state'])
            print('Status: ' + task_status['status'])
            if exception:
                print('Exception: \n' + textwrap.indent(exception, '    '))

    def _handle_communication(self):
        """ Periodically write feedback messages to the console.
        """
        while True:
            self._send()
            time.sleep(6)
