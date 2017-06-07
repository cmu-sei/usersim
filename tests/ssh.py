import api
import usersim

def testSSH():
    empty = {}
    missingUser = {
            "host": "me",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }
    wrongHost = {
            "host": 28,
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }
    wrongPort = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": "68",
            "policy": "AutoAdd"
            }
    blankPort = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": "",
            "policy": "AutoAdd"
            }
    blankHost = {
            "host": "",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }
    wrongPolicy = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoBAD"
            }
    missingPort = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "policy": "AutoAdd"
            }
    goodConfig = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }
    badKeyCases = [("empty", empty), ("missingUser", missingUser)]
    badValueCases = [("wrongHost", wrongHost), ("wrongPort", wrongPort), ("blankPort", blankPort),
                     ("blankHost", blankHost), ("wrongPolicy", wrongPolicy)]
    goodCases = [("missingPort", missingPort), ("goodConfig", goodConfig)]
    sim = usersim.UserSim(True)
    task = {'type': 'ssh', 'config' = None}

    for configName, config in badKeyCases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError("Incorrectly accepted %s" % configName)
        except KeyError:
            print("Correctly rejected %s" % configName)

    for configName, config in badValueCases:
        task['config'] = config
        try:
            api.new_task(task)
            raise AssertionError("Incorrectly accepted %s" % configName)
        except ValueError:
            print("Correctly rejected %s" configName)

    for configName, config in goodCases:
        task['config'] = config
        api.new_task(task)
        print('Correctly accepted %s' % configName)
        result = sim.cycle()
        if result:
            print('    Feedback from task:')
            print('    %s' % str(result))

if __name__ == '__main__':
    testSSH()
