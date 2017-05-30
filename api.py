""" Module which contains all public user simulator operations. All functions contained in this module are thread-safe
unless otherwise noted.
"""
import usersim
from usersim import States
import tasks


def new_task(config, start_paused=False):
    """ Inserts a new task into the user simulator.

    Arguments:
        task_config (dict): A dictionary with the following key:value pairs.
            'type':str
            'config':dict
        start_paused (bool): True if the new task should be paused initially, False otherwise.

    Raises:
        KeyError: See validate_config docstring.
        ValueError: See validate_config docstring.

    Returns:
        int: The new task's unique ID.
    """
    sim = usersim.UserSim()
    validate_config(config)
    task = tasks.task_dict[config['type']]
    t = task(config['config'])
    return sim.new_task(t, start_paused)

def pause_task(task_id):
    """ Pause a single task.

    Arguments:
        task_id (int): The task ID returned by an earlier call to new_task.

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
        task_id (int): The task ID returned by an earlier call to new_task.

    Returns:
        bool: True if the operation succeeded, False otherwise.
    """
    sim = usersim.UserSim()
    return sim.unpause_task(task_id)

def unpause_all():
    """ Unpause all currently scheduled tasks.
    """
    sim = usersim.UserSim()
    sim.unpause_all()

def status_task(task_id):
    """ Get the status of a single task.

    Arguments:
        task_id (int): The task ID returned by an earlier call to new_task.

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
        task_id (int): The task ID returned by an earlier call to new_task.

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
    """
    task = tasks.task_dict[config['type']]
    task.validate(config['config'])
