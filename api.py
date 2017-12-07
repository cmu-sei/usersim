# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

""" Module which contains all public user simulator operations. All functions contained in this module are thread-safe
unless otherwise noted.
"""
import re

import config as config_module
import externalvars
import usersim
from usersim import States
import tasks


def new_task(config, start_paused=False, reset=False):
    """ Inserts a new task into the user simulator.

    Arguments:
        task_config (dict): A dictionary with the following key:value pairs.
            'type':str
            'config':dict
        start_paused (bool): True if the new task should be paused initially, False otherwise.
        reset (bool): True if the simulator should be reset, False otherwise. This option should only be used
            for writing tests.

    Raises:
        KeyError: See validate_config docstring.
        ValueError: See validate_config docstring.

    Returns:
        int: The new task's unique ID.
    """
    sim = usersim.UserSim(reset)
    validated_config = validate_config(config)
    task = tasks.task_dict[config['type']]

    return sim.new_task(task, validated_config, start_paused)

def pause_task(task_id):
    """ Pause a single task.

    Arguments:
        task_id (int > 0): The task ID returned by an earlier call to new_task.

    Returns:
        bool: True if the operation succeeded, False otherwise.
    """
    sim = usersim.UserSim()
    return sim.pause_task(task_id)

def pause_all():
    """ Pause all currently scheduled tasks.
    """
    sim = usersim.UserSim()
    sim.pause_all()

def unpause_task(task_id):
    """ Unpause a single task.

    Arguments:
        task_id (int > 0): The task ID returned by an earlier call to new_task.

    Returns:
        bool: True if the operation succeeded, False otherwise.
    """
    sim = usersim.UserSim()
    return sim.unpause_task(task_id)

def unpause_all():
    """ Unpause all currently paused tasks.
    """
    sim = usersim.UserSim()
    sim.unpause_all()

def status_task(task_id):
    """ Get the status of a single task.

    Arguments:
        task_id (int > 0): The task ID returned by an earlier call to new_task.

    Returns:
        dict: A dictionary with the following key:value pairs:
            'id':int
            'type':str
            'state':str
            'status':str
    """
    sim = usersim.UserSim()
    return sim.status_task(task_id)

def status_all():
    """ Get a list of the status of all managed tasks.

    Returns:
        list of dicts: Each dictionary will have the following key:value pairs:
            'id':int
            'type':str
            'state':str
            'status':str
    """
    sim = usersim.UserSim()
    return sim.status_all()

def stop_task(task_id):
    """ Stop a single task.

    Arguments:
        task_id (int > 0): The task ID returned by an earlier call to new_task.

    Returns:
        bool: True if the operation succeeded, False otherwise.
    """
    sim = usersim.UserSim()
    return sim.stop_task(task_id)

def stop_all():
    """ Stop all tasks that are currently scheduled or paused.
    """
    sim = usersim.UserSim()
    sim.stop_all()

def validate_config(config):
    """ Validate a config dictionary without instantiating a Task subclass.

    Args:
        config (dict): A dictionary with the following key:value pairs.
            'type':str
            'config':dict

    Raises:
        KeyError: If a required key is missing from config or config['config'] or if the task type does not exist.
        ValueError: If the given value of an option under config['config'] is invalid.

    Returns:
        dict: The dictionary associated with config's 'config' key, after processing it with the given task's validate
            method. This does NOT include the 'type' and 'config' keys as above - only the actual configuration for the
            given task.
    """
    task = tasks.task_dict[config['type']]
    task_config = config['config']

    return task.validate(task_config)

def check_config(config, parameters, defaults):
    """ Asserts that all of the types in config match the types in the description strings in parameters. In addition,
    missing optional keys are added to the config from defaults.

    Args:
        config (dict): A dictionary to check. Should contain all keys from parameters['required']. Each key's value
            must be of the same type specified in that key's description string in parameters (both required and
            optional).
        parameters (dict): The return from a task.parameters call. Contains two keys, 'required' and 'optional', whose
            values are dict objects containing the keys that are required to be in config, and optional ones that may
            be in config. In these sub-dicts, the values are description strings that have at least one ':' (colon)
            character. Everything before the last ':' character is loaded as YAML (preferably compact), and it should
            describe the expected type structure of that particular parameter. For example, a list of strings should be
            written as follows:
                '[str]| blah blah your description here'
            A dictionary whose keys are ints and values are strs should be as follows:
                '{int: str}| some description here'
            Valid type strings (the 'str' or 'int' above) are the following:
                str, int, float, bool, any, number, task
            Where 'any' includes any of the first four, while 'task' indicates that the parameter is actually a task
            dict which should be validated with validate_config.
        defaults (dict): A dictionary whose keys are the same as the keys in parameters['optional'], and whose values
            are sane defaults for those parameters. These values should still have the same type as indicated by the
            description string in parameters.

    Raises:
        KeyError: If a key is missing from config. Exception message is the missing key.
        ValueError: If any parameter's value is invalid. Exception message is the reason it is invalid.

    Returns:
        dict: config with its parameters type-checked, and missing optional values inserted.
    """
    return config_module.validate(config, parameters['required'], parameters['optional'], defaults)

def get_tasks(filter_result=True):
    """ Get the tasks and their (human-readable) parameters currently available to this simulation. Certain special
    tasks will be filtered by default.

    Args:
        filter_result (bool): True - filters special tasks, False - no filter is applied.

    Returns:
        dict of dicts of dicts: A dictionary whose keys are task names, and whose values are dictionaries whose keys are
            'required' and 'optional', and whose values are dictionaries whose keys are the parameter name, and whose
            values are human-readable strings indicating what is expected for the parameter.
            There is also a new key at the same dictionary level as the 'required' and 'optional' keys, 'description'.
            The 'description' key contains a human-readable short summary of what the task tries to do, if such a
            description is provided by the task. Otherwise, it will be the string 'No description provided.'
    """
    special_tasks = [re.compile('task$'), re.compile('test'), re.compile('browser$')]

    available_tasks = {}

    for key in tasks.task_dict:
        for filtered in special_tasks:
            if filter_result and filtered.match(key):
                break
        else:
            # Else statements of a for-loop are triggered if a break was not triggered within the for-loop.
            parameters = tasks.task_dict[key].parameters()
            try:
                assert parameters is not None
            except AssertionError:
                raise AssertionError('{} parameters method returns None.'.format(key))
            available_tasks[key] = parameters
            doc = tasks.task_dict[key].__doc__ or 'No description provided.'
            available_tasks[key]['description'] = ' '.join(doc.strip().split())

    return available_tasks

def add_feedback(task_id, error):
    """ Create an additional feedback message. This will mostly be used from within threads supporting a main task, for
    example, managing interaction with an external program.

    Args:
        task_id (int): The task ID of the calling task. This can be accessed from within a task object by using
            self._task_id. If task_id < 1, no feedback will be generated.
        error (str): A description of the error, or a traceback.format_exc().
    """
    sim = usersim.UserSim()
    sim.add_feedback(task_id, error)

def external_lookup(var_name):
    """ Look up a variable external to the usersim. First looks at environment variables, then looks at VMWare guestinfo
    variables. Only returns a value for an exact match.

    Args:
        var_name (str): The name of the variable to lookup.

    Returns:
        str: Returns the value of the variable. If the variable is not found, returns an empty string.
    """
    return externalvars.lookup(var_name)
