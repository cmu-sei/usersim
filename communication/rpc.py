""" This file handles RPC communication between this usersim instance and a server. This offers more fine-grained
control over the usersim than any of the other communication options.
"""
import inspect
import threading
import time

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
    def __init__(self, feedback_queue, server_addr, server_port):
        self._feedback_queue = feedback_queue
        self._connection = rpyc.connect(server_addr, server_port, service=UserSimService)

        serve_thread = threading.Thread(target=self._connection.serve_all)
        serve_thread.daemon = True
        serve_thread.start()

        feedback_thread = threading.Thread(target=self._handle_communication)
        feedback_thread.daemon = True
        feedback_thread.start()

    def _handle_communication(self):
        """ Forward feedback messages to the server.
        """
        while True:
            while not self._feedback_queue.empty():
                status_dict, exception = self._feedback_queue.get()
                # Try to minimize spikes.
                time.sleep(1)
                self._connection.root.push_feedback(status_dict, exception)

            # Don't waste CPU cycles.
            time.sleep(10)
