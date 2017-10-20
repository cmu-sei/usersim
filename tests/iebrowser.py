# Ali Kidwai
# July 26, 2017
# Tests for InternetExplorer module in UserSim. Makes sure that InternetExplorer rejects incorrect configs and accepts
# correct configs. Prints output from correct configs.
import platform

import api
import usersim


def test_bad_key_cases(task, bad_key_cases):
    """ Used to test configs with missing keys. This function will raise an assertion error if validate incorrectly
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping 'type' to the task name (e.g. 'ssh')
        bad_key_cases: A list of tuples of the form ('configName', config). config should be missing at least one key.

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
        bad_value_cases: A list of tuples of the form ('configName', config). config should have at least one invalid
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
        good_cases: A list of tuples of the form ('configName, config'). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for config_name, config in good_cases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % config_name)

def run_test():
    if not platform.system() == 'Windows':
        return

    task = {'type': 'iebrowser', 'config': None}
    empty = {}
    none_sites = {'sites': None}
    empty_sites = {'sites': []}
    bad_sites = {'sites': ['www.cmu.edu', 1, True]}
    cmu = {'sites': ['www.cmu.edu']}
    google = {'sites': ['https://www.google.com']}
    wikipedia = {'sites': ['http://www.en.wikipedia.org/wiki/Main_Page']}
    amazon = {'sites': ['http://www.amazon.com']}
    cnn = {'sites': ['www.cnn.com']}
    bbc = {'sites': ['www.bbc.co.uk']}
    npr = {'sites': ['www.npr.org']}
    all_sites = {'sites': ['www.cmu.edu',
                           'https://www.google.com',
                           'http://en.wikipedia.org/wiki/Main_Page',
                           'http://www.amazon.com',
                           'www.cnn.com',
                           'www.bbc.co.uk',
                           'www.npr.org']}
    close = {'sites': ['www.cmu.edu'], 'close_browser': True}
    bad_key_cases = [('empty', empty)]
    bad_value_cases = [('none_sites', none_sites), ('empty_sites', empty_sites), ('bad_sites', bad_sites)]
    good_cases = [('cmu', cmu), ('google', google), ('wikipedia', wikipedia), ('amazon', amazon), ('cnn', cnn),
                  ('bbc', bbc), ('npr', npr), ('all_sites', all_sites), ('close', close)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()

