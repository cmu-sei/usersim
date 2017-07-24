import api
import usersim


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
    task = {'type': 'outlook', 'config': None}

    bad_value_cases = list()
    bad_value_cases.append(('link_str', {'open_links': 'f'}))
    bad_value_cases.append(('link_low', {'open_links': -5}))
    bad_value_cases.append(('link_high', {'open_links': 105}))
    bad_value_cases.append(('attach_str', {'open_attachments': 'f'}))
    bad_value_cases.append(('attach_low', {'open_attachments': -5}))
    bad_value_cases.append(('attach_high', {'open_attachments': 105}))
    bad_value_cases.append(('unread_int', {'unread': 105}))
    bad_value_cases.append(('display_messages_int', {'display_messages': 105}))
    bad_value_cases.append(('delete_handled_int', {'delete_handled': 105}))
    bad_value_cases.append(('nuke_outlook_int', {'nuke_outlook': 105}))
    bad_value_cases.append(('nuke_folders_int', {'nuke_folders': 105}))
    bad_value_cases.append(('regexes_int', {'regexes': 105}))
    bad_value_cases.append(('regexes_invalid_key', {'regexes': {25: dict()}}))
    bad_value_cases.append(('regexes_invalid_value', {'regexes': {'test': 523}}))

    good_cases = list()
    good_cases.append(('link', {'open_links': 50}))
    good_cases.append(('attach', {'open_attachments': 50}))
    good_cases.append(('unread', {'unread': True}))
    good_cases.append(('display_messages', {'display_messages': True}))
    good_cases.append(('delete_handled', {'delete_handled': True}))
    good_cases.append(('nuke_outlook', {'nuke_outlook': True}))
    good_cases.append(('nuke_folders', {'nuke_folders': ['Cant', 'Test', 'This']}))
    good_cases.append(('regexes', {'regexes': {'yayregex': {'type': 'test', 'config': {}}}}))
    good_cases.append(('empty', {'empty': {}}))

    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()
