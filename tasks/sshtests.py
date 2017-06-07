from ssh import *

def testSSH():
    badConfig1 = {}
    badConfig2 = {'host': ''}
    badConfig3 = {'host': 'io.smashthestack.org',
                   'user': 'level1',
                   'passwd': 'level1',
                   'cmdlist': ['cat README || cat readme', 'exit'],
                   'policy': ''}
    goodConfig1 = {'host': 'io.smashthestack.org',
                   'user': 'level1',
                   'passwd': 'level1',
                   'cmdlist': ['cat README || cat readme', 'exit']}

    try:
        ssh = SSH(badConfig1)
        raise AssertionError('Incorrectly accepted badConfig1')
    except KeyError:
        print('Correctly rejected badConfig1')
    try:
        ssh = SSH(badConfig2)
        raise AssertionError('Incorrectly accepted badConfig2')
    except KeyError:
        print('Correctly rejected badConfig2')
    try:
        ssh = SSH(badConfig3)
        raise AssertionError('Incorrectly accepted badConfig3')
    except ValueError:
        print('Correctly rejected badConfig3')

    try:
        ssh = SSH(goodConfig1)
        print('Correctly accepted goodConfig1')
    except:
        raise AssertionError('Incorrrectly rejected goodConfig1')

    print('Passed all tests!')

if __name__ == '__main__':
    testSSH()
