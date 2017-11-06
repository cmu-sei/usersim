# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

""" Handle communication over a Boost message queue in order to communicate using the XGA.

May not successfully import if boostmq could not be imported.
"""
import os
import threading
import time
import sys

import api
if sys.version_info.minor == 5:
    import communication.py35.boostmq as boostmq
    print(boostmq.__file__)
import config
from communication import common


LOG_PATH = os.path.join(os.path.expanduser('~'), 'feedback{}.log')
LOG_MAX = 5

def log_rotator():
    current_log = 1
    while True:
        # 2^20 = 1048576, which is 1MB.
        path = LOG_PATH.format(current_log)
        if os.path.exists(path) and os.path.getsize(path) > 1048576:
            # Current log is full, so rotate.
            current_log += 1
            if current_log > LOG_MAX:
                current_log = 1

            # Clear the log.
            open(LOG_PATH.format(current_log), 'w').close()

        yield LOG_PATH.format(current_log)

LOG_ROTATOR = log_rotator()

def log_error(status, exception):
    feedback = []
    feedback.append('Type: {}'.format(status['type']))
    feedback.append('ID: {}'.format(status['id']))
    feedback.append('State: {}'.format(status['state']))
    if status['status']:
        feedback.append('Status: {}'.format(status['status']))
    feedback.append('Exception: {}'.format(exception))
    feedback.append('=' * 40)

    try:
        with open(next(LOG_ROTATOR), 'a') as f:
            f.write('\n'.join(feedback) + '\n')
    except Exception as e:
        # If the log file fails, then the only remaining option is to write it to stdout...
        print(str(e))

class BoostCommunication(object):
    def __init__(self, feedback_queue):
        self._feedback_queue = feedback_queue
        self._config_mq = boostmq.MQ('config', 10, 50000)

        thread = threading.Thread(target=self._handle_communication)
        thread.daemon = True
        thread.start()

    def _receive(self):
        """ Check if there are any messages available. If an invalid message is received, sends a feedback message
        indicating the error and the portion of the message that was received.

        Returns:
            None: If no (valid) messages are available.
            list of dicts: See config.string_to_python
        """
        message = ''
        last_error = ''

        while True:
            # Need to stitch messages together if a config is too large for the message queue.
            more = self._config_mq.receivequeue_noblock()
            if more:
                print('Got data from Boost MQ.')

            if message and not more:
                feedback_message = last_error + '\n\n' + message
                print(feedback_message)
                # Even though we're not sending feedback, this is pretty harmless and means we don't need to figure out
                # where to add a feedback message to the queue if that changes.
                self._feedback_queue.put((common.api_exception_status, feedback_message))
            if not more:
                # If there's nothing else, go to sleep for a while.
                break

            message += more

            try:
                new_config = config.string_to_python(message)
            except ValueError:
                print('Got bad configuration from Boost MQ.')
                # Message may need to be stitched together. Give plenty of time for the next part to be
                # added to the shared message queue.
                time.sleep(.5)
                continue
            else:
                return new_config

    def _send(self):
        """ If any feedback messages are queued, construct feedback messages in the format the XGA is expecting and
        send them.
        """
        while not self._feedback_queue.empty():
            # Put them in a log file, since there's nothing to listen for these, currently.
            status, exception = self._feedback_queue.get()
            if not exception:
                continue
            log_error(status, exception)

    def _handle_communication(self):
        """ Periodically check if there are any new config files available or if there is any feedback that should be
        forwarded.
        """
        while True:
            new_config = self._receive()
            if new_config:
                available_tasks = api.get_tasks(False)

                for task in new_config:
                    # As in the _receive method, it's okay for the feedback messages in here to stay in case feedback is
                    # used with boost in later versions.
                    if task['type'] not in available_tasks:
                        self._feedback_queue.put((common.api_exception_status, 'task ' + task['type'] + ' does not '
                            'exist in the current build'))
                        continue

                    try:
                        api.new_task(task)
                    except KeyError as e:
                        self._feedback_queue.put((common.api_exception_status, 'task ' + task['type'] + ' missing '
                            'required key %s from its configuration' % e.message))
                    except ValueError as e:
                        self._feedback_queue.put((common.api_exception_status, 'task ' + task['type'] + ' has at least '
                            'one bad value for a config option:\n%s' % e.message))

            self._send()

            # So the CPU isn't running at 100%.
            time.sleep(5)
