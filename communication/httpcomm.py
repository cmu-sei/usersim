# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import inspect
import threading
import time

import requests

import api


class HTTPCommunication(object):
    def __init__(self, feedback_queue, ip_addr, port, name, groups):
        print('\nIP Address: {}\nPort: {}\nName: {}\nGroups: {}'.format(ip_addr, port, name, groups))

        self._feedback_queue = feedback_queue
        self._server_addr = ip_addr
        self._server_port = port
        self._name = name
        self._groups = groups
        self._api_funcs = dict(inspect.getmembers(api, inspect.isfunction))

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
                response = requests.get('http://{}:{}/instructions/agent'.format(self._server_addr, self._server_port),
                                        json={'name': self._name})
            except requests.exceptions.RequestException as e:
                print(str(e))
            else:
                # TODO: Actually execute the instruction.
                print('Polled server for new instructions. Got the following:')
                instructions = response.json()
                print(instructions)
                for instruction in instructions:
                    func_name = instruction['function']
                    func = self._api_funcs[func_name]
                    kwargs = instruction['arguments']
                    func(**kwargs)

            # TODO: Get from command line, add randomness to spread out the requests.
            time.sleep(10)

    def send_feedback(self):
        pass
