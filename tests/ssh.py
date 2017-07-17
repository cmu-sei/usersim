# Ali Kidwai
# June 16, 2017
# Tests for SSH module for UserSim. Makes sure that SSH rejects incorrect configs and accepts correct configs. Prints
# output from correct configs.

import api
import usersim

def test_bad_key_cases(task, bad_key_cases):
    """ Used to test configs with missing keys. This function will raise an assertion error if validate incorrectly
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        bad_key_cases: A list of tuples of the form ("config_name", config). config should be missing at least one key.

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
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        bad_value_cases: A list of tuples of the form ("config_name", config). config should have at least one invalid
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
    """ Used to test properly formatted configs.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        good_cases: A list of tuples of the form ("config_name, config"). config should be properly formatted.
    """
    for config_name, config in good_cases:
        task['config'] = config
        if config['host']:
            print('Trying to connect to %s in test configuration...' % config['host'])
            sim = usersim.UserSim(True)
            api.new_task(task)
            result = sim.cycle()
            for item in result:
                print(item)
        else:
            print('No host specified for test. Cannot test connectivity.')
        print('Correctly accepted %s' % config_name)

def test_ssh():
    task = {'type': 'ssh', 'config': None}
    empty = {}
    missing_user = {
            'host': 'me',
            'password': 'badpassword',
            'command_list': ['echo hello']
            }
    wrong_host = {
            'host': 28,
            'user': 'admin',
            'password': 'badpassword',
            'command_list': ['echo hello']
            }
    wrong_port = {
            'host': 'me',
            'user': 'admin',
            'password': 'badpassword',
            'command_list': ['echo hello'],
            'port': '68'
            }
    blank_port = {
            'host': 'me',
            'user': 'admin',
            'password': 'badpassword',
            'command_list': ['echo hello'],
            'port': str()
            }
    blank_host = {
            'host': str(),
            'user': 'admin',
            'password': 'badpassword',
            'command_list': ['echo hello']
            }
    wrong_policy = {
            'host': 'me',
            'user': 'admin',
            'password': 'badpassword',
            'command_list': ['echo hello'],
            'policy': 'AutoBAD'
            }
    missing_opts = {
            'host': '',
            'user': '',
            'password': '',
            'command_list': ['echo hello', 'ls', 'exit']
            }
    good_config = {
            'host': '',
            'user': '',
            'password': '',
            'command_list': ['echo hello', 'ls', 'exit'],
            'port': 22,
            'policy': 'AutoAdd'
            }
    bad_key_cases = [('empty', empty), ('missing_user', missing_user)]
    bad_value_cases = [('wrong_host', wrong_host), ('wrong_port', wrong_port), ('blank_port', blank_port),
                     ('blank_host', blank_host), ('wrong_policy', wrong_policy)]
    good_cases = [('missing_opts', missing_opts), ('good_config', good_config)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    test_ssh()
