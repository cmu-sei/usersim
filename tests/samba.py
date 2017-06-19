import api
import usersim

def testBadKeyCases(task, badKeyCases):
    """ Used to test configs with missing keys. This function will raise an assertion error if validate incorrectly 
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        badKeyCases: A list of tuples of the form ("configName", config). config should be missing at least one key.

    Raises:
        AssertionError: If api.new_task does not raise a KeyError
    """
    for configName, config in badKeyCases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError('Incorrectly accepted %s' % configName)
        except KeyError:
            print("Correctly rejected %s" % configName)

def testBadValueCases(task, badValueCases):
    """ Used to test configs with invalid values. This function will raise an assertion error if validate incorrectly 
    accepts a bad config dictionary.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        badValueCases: A list of tuples of the form ("configName", config). config should have at least one invalid 
            value.

    Raises:
        AssertionError: If api.new_task does not raise a ValueError
    """
    for configName, config in badValueCases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError('Incorrectly accepted %s' % configName)
        except ValueError:
            print("Correctly rejected %s" % configName)

def testGoodCases(task, goodCases):
    """ Used to test properly formatted configs. Prints feedback from the task.

    Args:
        task: A task dictionary mapping "type" to the task name (e.g. "ssh")
        goodCases: A list of tuples of the form ("configName, config"). config should be properly formatted.
    """
    sim = usersim.UserSim(True)
    for configName, config in goodCases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % configName)
        sim.cycle()
        result = sim.cycle()
        if result:
            print('    Feedback from task:')
            print('    %s' % str(result))

def testSamba():
    task = {'type': 'samba', 'config': None}
    empty = {}
    noneAddress = {'address': None}
    emptyAddress = {'address': ''}
    nonePort = {'address': 'localhost', 'port': None}
    badPort = {'address': 'localhost', 'port': 10000000000}
    badFiles = {'address': 'localhost', 'files': [None, 1, "README"]}
    random1 = {'address': 'localhost'}
    random2 = {'address': 'localhost', 'files': []}
    authenticated = {'address': 'localhost', 'user': '', 'passwd': ''}
    complete = {'address': 'localhost', 'user': '', 'passwd': '', 'files': []}
    badKeyCases = [('empty', empty)]
    badValueCases = [('noneAddress', noneAddress), ('nonePort', nonePort), ('badPort', badPort), ('badFiles', badFiles)]
    goodCases = [('random1', random1), ('random2', random2), ('authenticated', authenticated), ('complete', complete)]
    testBadKeyCases(task, badKeyCases)
    testBadValueCases(task, badValueCases)
    testGoodCases(task, goodCases)

if __name__ == '__main__':
    testSamba()
