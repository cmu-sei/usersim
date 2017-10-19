# Ali Kidwai
# July 18, 2017
# Tests for Samba module for UserSim. Makes sure that SSH rejects incorrect configs and accepts correct configs. Prints
# output from correct configs. Be sure to update test cases with the relevant info for your Samba test server.

import api
import usersim

def test_bad_key_cases(task, bad_key_cases):
    """ Used to test configs with missing keys. This function will raise an assertion error if validate incorrectly
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping 'type' to the task name (e.g. 'ssh')
        bad_key_cases: A list of tuples of the form ('config_name', config). config should be missing at least one key.

    Raises:
        AssertionError: If api.new_task does not raise a KeyError
    """
    for config_name, config in bad_key_cases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError('Incorrectly accepted %s' % config_name)
        except KeyError:
            print('Correctly rejected %s' % config_name)

def test_bad_value_cases(task, bad_value_cases):
    """ Used to test configs with invalid values. This function will raise an assertion error if validate incorrectly
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping 'type' to the task name (e.g. 'ssh')
        bad_value_cases: A list of tuples of the form ('config_name', config). config should have at least one invalid
            value.

    Raises:
        AssertionError: If api.new_task does not raise a ValueError
    """
    for config_name, config in bad_value_cases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError('Incorrectly accepted %s' % config_name)
        except ValueError:
            print('Correctly rejected %s' % config_name)

def test_good_cases(task, good_cases):
    """ Used to test properly formatted configs. Prints feedback from the task.

    Args:
        task: A task dictionary mapping 'type' to the task name (e.g. 'ssh')
        good_cases: A list of tuples of the form ('config_name', config). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for config_name, config in good_cases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % config_name)
        #result = sim.cycle()
        #for task_id, exception in result:
        #    if not exception:
        #        continue
        #    print(exception)
        #    print('*'*80)

def run_test():
    task = {'type': 'samba', 'config': None}
    empty = {}
    none_address = {'address': None}
    empty_address = {'address': ''}
    none_port = {'address': '', 'port': None}
    bad_port = {'address': 'localhost', 'port': 1000000000}
    bad_files = {'address': 'localhost', 'files': [None, 1, 'README']}
    echo1 = {'address': 'localhost', 'user': 'blah', 'password': 'blah'}
    echo2 = {'address': 'localhost', 'files': [], 'user': 'blah', 'password': 'blah'}
    authenticated = {'address': 'localhost', 'user': 'blah', 'password': 'blah'}
    complete = {'address': 'localhost', 'user': 'blah', 'password': 'blah',
            'files': ['Users/Win10/Documents/testshare/blah.txt'], 'write_dir': '.'}
    bad_key_cases = [('empty', empty)]
    bad_value_cases = [('none_address', none_address), ('none_port', none_port), ('bad_port', bad_port),
                       ('bad_files', bad_files)]
    good_cases = [('echo1', echo1), ('echo2', echo2), ('authenticated', authenticated), ('complete', complete)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()
