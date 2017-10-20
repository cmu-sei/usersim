# Ali Kidwai
# June 16, 2017
# Tests for FTP module for UserSim. Makes sure that FTP rejects incorrect configs and accepts correct configs. Prints
# output from correct configs.
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
        good_cases: A list of tuples of the form ('config_name, config'). config should be properly formatted.
    """
    for config_name, config in good_cases:
        task['config'] = config
        sim = usersim.UserSim(True)
        api.new_task(task)
        print('Correctly accepted %s' % config_name)

def run_test():
    task = {'type': 'ftp', 'config': None}
    empty = {}
    missing_site = {'file': '1KB.zip'}
    missing_file = {'site': 'speedtest.tele2.net'}
    none_args = {'site': None, 'file': None}
    blank_site = {'site': '', 'file': '1KB.zip'}
    blank_file = {'site': 'speedtest.tele2.net', 'file': ''}
    missing_opts = {'site': 'speedtest.tele2.net', 'file': '1KB.zip'}
    missing_password = {'site': 'speedtest.tele2.net', 'file': '100KB.zip', 'user': 'anonymous'}
    complete_config = {'site': 'speedtest.tele2.net', 'file': '512KB.zip',
                      'user': 'anonymous', 'password': 'anonymous@'}
    bad_key_cases = [('empty', empty), ('missing_site', missing_site), ('missing_file', missing_file)]
    bad_value_cases = [('none_args', none_args), ('blank_site', blank_site), ('blank_file', blank_file)]
    good_cases = [('missing_opts', missing_opts),
                  ('missing_password', missing_password),
                  ('complete_config', complete_config)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()
