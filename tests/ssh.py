# Ali Kidwai
# June 8, 2017
# Tests for SSH module for UserSim. Makes sure that SSH rejects incorrect configs and accepts correct configs. Prints
# output from correct configs.

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

    Returns:
        None
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

    Returns:
        None
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

    Returns:
        None
    """
    sim = usersim.UserSim(True)
    for configName, config in goodCases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % configName)
        result = sim.cycle()
        if result:
            print('    Feedback from task:')
            print('    %s' % str(result))

def testSSH():
    task = {'type': 'ssh', 'config': None}
    empty = {}
    missingUser = {
            "host": "me",
            "passwd": "badpassword",
            "cmdlist": ["echo hello"]
            }
    wrongHost = {
            "host": 28,
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": ["echo hello"]
            }
    wrongPort = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": ["echo hello"],
            "port": "68"
            }
    blankPort = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": ["echo hello"],
            "port": ""
            }
    blankHost = {
            "host": "",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": ["echo hello"]
            }
    wrongPolicy = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": ["echo hello"],
            "policy": "AutoBAD"
            }
    missingOpts = {
            "host": "unix.andrew.cmu.edu",
            "user": "",
            "passwd": "",
            "cmdlist": ["echo hello", "ls", "exit"]
            }
    goodConfig = {
            "host": "unix.andrew.cmu.edu",
            "user": "",
            "passwd": "",
            "cmdlist": ["echo hello", "ls", "exit"],
            "port": 68,
            "policy": "AutoAdd"
            }
    badKeyCases = [("empty", empty), ("missingUser", missingUser)]
    badValueCases = [("wrongHost", wrongHost), ("wrongPort", wrongPort), ("blankPort", blankPort),
                     ("blankHost", blankHost), ("wrongPolicy", wrongPolicy)]
    goodCases = [("missingOpts", missingOpts), ("goodConfig", goodConfig)]
    testBadKeyCases(task, badKeyCases)
    testBadValueCases(task, badValueCases)
    testGoodCases(task, goodCases)

if __name__ == '__main__':
    testSSH()
