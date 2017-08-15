""" Module which contains all public user simulator operations. All functions contained in this module are thread-safe
unless otherwise noted.
"""
import re

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

def get_tasks(filter_result=True):
    """ Get the tasks and their (human-readable) parameters currently available to this simulation. Certain special
    tasks will be filtered by default.

    Args:
        filter_result (bool): True - filters special tasks, False - no filter is applied.

    Returns:
        dict of dicts of dicts: A dictionary whose keys are task names, and whose values are dictionaries whose keys are
            'required' and 'optional', and whose values are dictionaries whose keys are the parameter name, and whose
            values are human-readable strings indicating what is expected for the parameter.
    """
    special_tasks = [re.compile('task$'), re.compile('test')]

    available_tasks = dict()

    for key in tasks.task_dict:
        for filtered in special_tasks:
            if filter_result and filtered.match(key):
                break
        else:
            # Else statements of a for-loop are triggered if a break was not triggered within the for-loop.
            available_tasks[key] = tasks.task_dict[key].parameters()

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
