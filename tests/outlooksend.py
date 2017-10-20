import platform

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
    """ Test configs with invalid values.

    Args:
        task (dict): A task config dict. task['config'] will be overwritten.
        bad_value_cases (list(tuple)): List of tuples of the form ('config_name', config), where config
            contains a key:value pair with an invalid value.
    """
    for config_name, config in bad_value_cases:
        task['config'] = config
        try:
            api.new_task(task)
        except ValueError:
            print('Correctly rejected %s' % config_name)
        else:
            raise AssertionError('Incorrectly accepted %s' % config_name)


def test_good_cases(task, good_cases):
    """ Test properly formatted configs.

    Args:
        task (dict): A task config dict. task['config'] will be overwritten.
        good_cases (list(tuple)): List of tuples of the form ('config_name', config), where config
            is a valid config for the task.
    """
    for config_name, config in good_cases:
        task['config'] = config
        sim = usersim.UserSim(True)
        api.new_task(task)
        result = sim.cycle()
        for item in result:
            print(item)
        print('Correctly accepted %s' % config_name)

def run_test():
    if not platform.system() == 'Windows':
        return
    task = {'type': 'outlooksend', 'config': None}

    everything = {'username': 'example',
                  'destination': 'example',
                  'subject': 'example',
                  'body': 'example',
                  'attachments': ['test1', 'test2'],
                  'dynamic': True}

    # Create missing key configs.
    nousername = {}
    nousername.update(everything)
    del nousername['username']

    nodestination = {}
    nodestination.update(everything)
    del nodestination['destination']

    nosubject = {}
    nosubject.update(everything)
    del nosubject['subject']

    nobody = {}
    nobody.update(everything)
    del nobody['body']

    bad_key_cases = []
    bad_key_cases.append(('nothing', {}))
    bad_key_cases.append(('nousername', nousername))
    bad_key_cases.append(('nodestination', nodestination))
    bad_key_cases.append(('nosubject', nosubject))
    bad_key_cases.append(('nobody', nobody))

    # Create configs with bad values.
    badusername = {}
    badusername.update(everything)
    badusername['username'] = 0

    baddestination = {}
    baddestination.update(everything)
    baddestination['destination'] = 0

    badsubject = {}
    badsubject.update(everything)
    badsubject['subject'] = 0

    badbody = {}
    badbody.update(everything)
    badbody['body'] = 0

    badattachments = {}
    badattachments.update(everything)
    badattachments['attachments'] = 0

    baddynamic = {}
    baddynamic.update(everything)
    baddynamic['dynamic'] = 0

    bad_value_cases = []
    bad_value_cases.append(badusername)
    bad_value_cases.append(baddestination)
    bad_value_cases.append(badsubject)
    bad_value_cases.append(badbody)
    bad_value_cases.append(badattachments)
    bad_value_cases.append(baddynamic)

    # Create valid configs.
    attachments = {}
    attachments.update(everything)
    del attachments['dynamic']

    dynamic = {}
    dynamic.update(everything)
    del dynamic['attachments']

    nooptionals = {}
    nooptionals.update(everything)
    del nooptionals['attachments']
    del nooptionals['dynamic']

    good_cases = []
    good_cases.append(everything)
    good_cases.append(attachments)
    good_cases.append(dynamic)
    good_cases.append(nooptionals)

    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()
