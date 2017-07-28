# Ali Kidwai
# July 20, 2017
# Tests for Word module for UserSim. Makes sure that Word rejects incorrect configs and accepts correct configs. Prints
# output from correct configs.

import api
import usersim

def test_bad_value_cases(task, bad_value_cases):
    """ Used to test configs with invalid values. This function will raise an assertion error if validate incorrectly
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        badValueCases: A list of tuples of the form ("config_name", config). config should have at least one invalid
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
            print("Correctly rejected %s" % config_name)

def test_good_cases(task, good_cases):
    """ Used to test properly formatted configs. Prints feedback from the task.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        goodCases: A list of tuples of the form ("config_name", config). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for config_name, config in good_cases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % config_name)
        sim.cycle()
        result = sim.cycle()
        if result:
            print('    Feedback from task:')
            print('    %s' % str(result))

def run_test():
    task = {'type': 'word', 'config': None}
    bad_filetype = {'file_types': ['docx', 'exe']}
    empty = {}
    empty_source = {'text_source': ''}
    custom_source = {'text_source': 'text.txt'}
    xml = {'file_types': ['xml']}
    modify = {'new_doc': False}
    no_cleanup = {'cleanup': False}
    complete = {'text_source': 'text.txt', 'file_types': ['xml', 'rtf'], 'new_doc': False, 'cleanup': False}
    bad_value_cases = [('bad_filetype', bad_filetype)]
    good_cases = [('empty', empty), ('custom_source', custom_source), ('xml', xml), ('modify', modify),
                 ('no_cleanup', no_cleanup), ('complete', complete)]
    test_bad_value_cases(task, bad_value_cases)
    test_good_cases(task, good_cases)

if __name__ == '__main__':
    run_test()
