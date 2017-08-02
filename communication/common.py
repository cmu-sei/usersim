""" Code that is shared by more than one communication method.
"""
import api


# Used for sending error feedback messages in legacy communication methods.
api_exception_status = {'id': 0, 'type': 'apiexception', 'state': api.States.UNKNOWN, 'status': str()}
