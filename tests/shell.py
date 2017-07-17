# Ali Kidwai
# June 16, 2017
# Tests for Shell module in UserSim. Makes sure that Shell rejects incorrect configs and accepts correct configs. Prints
# output from correct configs.

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
        bad_value_cases: A list of tuples of the form ("configName", config). config should have at least one invalid
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
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        good_cases: A list of tuples of the form ("configName, config"). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for config_name, config in good_cases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % config_name)
        result = sim.cycle()
        if result:
            print('    Feedback from task:')
            print('    %s' % str(result))

def run_test():
    task = {'type': 'shell', 'config': None}
    empty = {}
    no_commands = {'commands': None}
    empty_commands_list = {'commands': []}
    int_in_commands_list = {'commands': ['cat', 'dog', 42]}
    good_config = {'commands': ['ls -la', 'echo hello &']}
    script_config = {'commands': ['ls -la', 'echo hello &'], 'script': True}
    bad_key_cases = [('empty', empty)]
    bad_value_cases = [('no_commands', no_commands), ('empty_commands_list', empty_commands_list),
                     ('int_in_commands_list', int_in_commands_list)]
    good_cases = [('good_config', good_config), ('script_config', script_config)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()
