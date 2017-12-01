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
        register_thread = threading.Thread(target=self.register)
        register_thread.daemon = True
        register_thread.start()

        poll_thread = threading.Thread(target=self.get_instructions)
        poll_thread.daemon = True
        poll_thread.start()

        feedback_thread = threading.Thread(target=self.send_feedback)
        feedback_thread.daemon = True
        feedback_thread.start()

    def get_instructions(self):
        return_vals = []
        while True:
            try:
                response = requests.get('http://{}:{}/instructions/agent'.format(self._server_addr, self._server_port),
                                        json={'name': self._name})
            except requests.exceptions.RequestException as e:
                print(str(e))
            else:
                instructions = response.json()
                for instruction in instructions:
                    try:
                        func_name = instruction['function']
                        func = self._api_funcs[func_name]
                        kwargs = instruction['arguments']
                        value = func(**kwargs)
                    except Exception as e:
                        value = str(e)
                    # TODO: Probably want to separate exceptions and normal values.
                    return_vals.append({'id': instruction['id'], 'value': value})

                if return_vals:
                    submissions = {'submissions': return_vals, 'name': self._name}
                    try:
                        requests.post('http://{}:{}/return/agent'.format(self._server_addr, self._server_port),
                                      json=submissions)
                    except requests.exceptions.RequestException as e:
                        print(str(e))
                    else:
                        # If we can submit to the server, then we don't need to hold onto them anymore. Otherwise, we
                        # hold them until we can contact the server again.
                        return_vals = []


            # TODO: Get from command line, add randomness to spread out the requests.
            time.sleep(10)

    def send_feedback(self):
        while True:
            fb_list = []
            while not self._feedback_queue.empty():
                fb_list.append(self._feedback_queue.get())

            fb_dict = {'name': self._name, 'feedback': fb_list}

            requests.post('http://{}:{}/feedback/agent'.format(self._server_addr, self._server_port), json=fb_dict)

            time.sleep(30)

    def register(self):
        while True:
            try:
                response = requests.post('http://{}:{}/register/agent'.format(self._server_addr, self._server_port),
                                         json={'name': self._name, 'groups': self._groups})
            except requests.exceptions.RequestException as e:
                print(str(e))
                # Keep trying until we initially register.
                time.sleep(30)
            else:
                return
