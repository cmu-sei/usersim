import usersim
from usersim import States
import tasks


def new_task(task_config, start_paused=False):
    """ Inserts a new task into the user simulator.

    Arguments:
        task_config (dict): A dictionary with the following key:value pairs.
            'type':str
            'config':dict
        start_paused (bool): True if the new task should be paused initially, False otherwise.

    Returns:
        int: The new task's unique ID.
    """
    us = usersim.UserSim()
    new_task = tasks.task_dict[task_config['type']].config(task_config['config'])
    return us.new_task(new_task, start_paused)

def pause_task(task_id):
    pass

def pause_all():
    pass

def unpause_task(task_id):
    pass

def unpause_all():
    pass

def status_task(task_id):
    pass

def status_all():
    pass

def stop_task(task_id):
    pass

def stop_all():
    pass
