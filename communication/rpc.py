# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

""" This file handles RPC communication between this usersim instance and a server. This offers more fine-grained
control over the usersim than any of the other communication options.
"""
import inspect
import platform
import random
import threading
import time
import traceback

import rpyc

import api

class UserSimService(rpyc.Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Expose all API functions dynamically.
        api_functions = inspect.getmembers(api, inspect.isfunction)

        for function_name, function in api_functions:
            setattr(self.__class__, 'exposed_' + function_name, staticmethod(function))

class RPCCommunication(object):
    def __init__(self, feedback_queue, server_addr, server_port, name):
        self._feedback_queue = feedback_queue
        self._server_addr = server_addr
        self._server_port = server_port
        self._name = name

        serve_thread = threading.Thread(target=self.serve_all)
        serve_thread.daemon = True
        serve_thread.start()

        feedback_thread = threading.Thread(target=self._handle_communication)
        feedback_thread.daemon = True
        feedback_thread.start()

    def serve_all(self):
        while True:
            # If we're having trouble talking to the server, give it a bit of time before trying again.
            time.sleep(10)

            try:
                self._connection = rpyc.connect(self._server_addr, self._server_port, service=UserSimService)
                if self._name:
                    self._connection.root.register(self._name, platform.system())
            except Exception:
                print('Exception raised on attempt to connect and register with the server.\n', traceback.format_exc())
                continue

            try:
                while True:
                    served = self._connection.serve(0)
                    if not served:
                        time.sleep(0.1)
            except Exception:
                print('Exception raised while polling the RPC socket. Trying to reconnect.\n', traceback.format_exc())
            finally:
                self._connection.close()

    def _handle_communication(self):
        """ Forward feedback messages to the server.
        """
        while True:
            fb_list = []
            while not self._feedback_queue.empty():
                fb_message = self._feedback_queue.get()
                fb_list.append(fb_message)

            try:
                if fb_list:
                    self._connection.root.bulk_feedback(fb_list)
            except Exception:
                print('Exception raised while attempting to push feedback to the server.\n', traceback.format_exc())
                # Don't drop feedback messages if possible.
                for fb_message in fb_list:
                    self._feedback_queue.put(fb_message)

            # Using a random int here in order to avoid syncing client feedback sends, hopefully reducing peak load on
            # the server.
            sleep_duration = random.randint(5, 115)
            time.sleep(sleep_duration)
