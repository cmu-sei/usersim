# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import threading
import time

import requests

class HTTPCommunication(object):
    def __init__(self, feedback_queue, ip_addr, port, name, groups):
        print('\nIP Address: {}\nPort: {}\nName: {}\nGroups: {}'.format(ip_addr, port, name, groups))

        self._feedback_queue = feedback_queue
        self._server_addr = ip_addr
        self._server_port = port
        self._name = name
        self._groups = groups

        # TODO: Put a check within get_instructions() to see if we need to reregister on the server, and move this
        # there.
        try:
            response = requests.post('http://{}:{}/register/agent'.format(ip_addr, port),
                                     json={'name': name, 'groups': groups})
        except requests.exceptions.RequestException as e:
            print(str(e))
            return

        poll_thread = threading.Thread(target=self.get_instructions)
        poll_thread.daemon = True
        poll_thread.start()

        feedback_thread = threading.Thread(target=self.send_feedback)
        feedback_thread.daemon = True
        feedback_thread.start()

    def get_instructions(self):
        while True:
            try:
                response = requests.get('http://{}:{}/instructions'.format(self._server_addr, self._server_port),
                                        json={'name': self._name})
            except requests.exceptions.RequestException as e:
                print(str(e))
            else:
                # TODO: Actually execute the instruction.
                print('Polled server for new instructions. Got the following:')
                print(response.text)

            # TODO: Get from command line, add randomness to spread out the requests.
            time.sleep(10)

    def send_feedback(self):
        pass
