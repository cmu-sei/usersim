# Ali Kidwai
# June 22, 2017

import api
import usersim

def test_bad_key_cases(task, bad_key_cases):
    """ Used to test configs with missing keys. This function will raise an assertion error if validate incorrectly 
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        bad_key_cases: A list of tuples of the form ("configName", config). config should be missing at least one key.

    Raises:
        AssertionError: If api.new_task does not raise a KeyError
    """
    for configName, config in bad_key_cases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError('Incorrectly accepted %s' % configName)
        except KeyError:
            print("Correctly rejected %s" % configName)

def test_bad_value_cases(task, bad_value_cases):
    """ Used to test configs with invalid values. This function will raise an assertion error if validate incorrectly 
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        bad_value_cases: A list of tuples of the form ("configName", config). config should have at least one invalid 
            value.

    Raises:
        AssertionError: If api.new_task does not raise a ValueError
    """
    for configName, config in bad_value_cases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError('Incorrectly accepted %s' % configName)
        except ValueError:
            print("Correctly rejected %s" % configName)

def test_good_cases(task, good_cases):
    """ Used to test properly formatted configs. Prints feedback from the task.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        good_cases: A list of tuples of the form ("configName", config). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for configName, config in good_cases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % configName)
        sim.cycle()
        result = sim.cycle()
        if result:
            print('    Feedback from task:')
            print('    %s' % str(result))

def test_samba():
    task = {'type': 'samba', 'config': None}
    empty = {}
    none_address = {'address': None}
    empty_address = {'address': ''}
    none_port = {'address': 'localhost', 'port': None}
    bad_port = {'address': 'localhost', 'port': 1000000000}
    bad_files = {'address': 'localhost', 'files': [None, 1, "README"]}
    random1 = {'address': 'localhost'}
    random2 = {'address': 'localhost', 'files': []}
    authenticated = {'address': 'localhost', 'user': '', 'passwd': ''}
    complete = {'address': 'localhost', 'user': '', 'passwd': '', 'files': []}
    bad_key_cases = [('empty', empty)]
    bad_value_cases = [('noneAddress', noneAddress), ('nonePort', nonePort), ('badPort', badPort),
                       ('badFiles', badFiles)]
    good_cases = [('random1', random1), ('random2', random2), ('authenticated', authenticated), ('complete', complete)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    test_samba()
