# Ali Kidwai
# August 3, 2017
# Tests for SMTP module in UserSim. Makes sure that SMTP rejects incorrect configs and accepts correct configs. Prints
# output from correct configs. Be sure to update test cases with the relevant info for your e-mail server.

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
        good_cases: A list of tuples of the form ("configName", config). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for config_name, config in good_cases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % config_name)
        #result = sim.cycle()
        #if result:
        #    print('    Feedback from task:')
        #    print('    %s' % str(result))

def run_test():
    task = {'type': 'smtp', 'config': None}
    empty = {}
    no_user = {'destinations': ['testuser1@localhost'],
               'mail_server': 'ubuntu'}
    no_dest = {'email_addr': 'akidwai@localhost',
               'mail_server': 'ubuntu'}
    no_site = {'email_addr': 'akidwai@localhost',
               'destinations': ['testuser1@localhost']}
    bad_user = {'email_addr': None,
                'destinations': ['testuser1@localhost'],
                'mail_server': 'ubuntu'}
    bad_dest1 = {'email_addr': 'akidwai@localhost',
                 'destinations': None,
                 'mail_server': 'ubuntu'}
    bad_dest2 = {'email_addr': 'akidwai@localhost',
                 'destinations': ['testuser1@localhost', None, 3],
                 'mail_server': 'ubuntu'}
    bad_site = {'email_addr': 'akidwai@localhost',
                'destinations': ['testuser1@localhost'],
                'mail_server': None}
    random_msg_and_subject = {'email_addr': 'akidwai@localhost',
                              'destinations': ['testuser1@localhost'],
                              'mail_server': 'ubuntu'}
    random_msg = {'email_addr': 'akidwai@localhost',
                  'destinations': ['testuser1@localhost'],
                  'mail_server': 'ubuntu',
                  'subjects': ['Test message subject']}
    random_subject = {'email_addr': 'akidwai@localhost',
                      'destinations': ['testuser1@localhost'],
                      'mail_server': 'ubuntu',
                      'messages': ['Test message body']}
    complete = {'email_addr': 'akidwai@localhost',
                'destinations': ['testuser1@localhost', 'testuser2@localhost'],
                'mail_server': 'ubuntu',
                'messages': ['Test message body 1', 'Test message body 2'],
                'subjects': ['Test message subject 1', 'Test message subject 2']}
    encrypted = {'email_addr': 'akidwai@localhost',
                 'destinations': ['testuser1@localhost', 'testuser2@localhost'],
                 'mail_server': 'ubuntu',
                 'messages': ['Test message body 1', 'Test message body 2'],
                 'subjects': ['Test message subject 1', 'Test message subject 2'],
                 'encrypt': True}
    bad_key_cases = [('empty', empty), ('no_user', no_user), ('no_dest', no_dest), ('no_site', no_site)]
    bad_value_cases = [('bad_user', bad_user), ('bad_dest1', bad_dest1), ('bad_dest2', bad_dest2),
                       ('bad_site', bad_site)]
    good_cases = [('random_msg_and_subject', random_msg_and_subject), ('random_msg', random_msg),
                  ('random_subject', random_subject), ('complete', complete), ('encrypted', encrypted)]
    test_bad_key_cases(task, bad_key_cases)
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()

