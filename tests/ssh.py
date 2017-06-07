import api
import usersim

def run_test(sim, input_dict):
    task_id = api.new_task(config)
    result = sim.cycle()
    if len(result) > 1:
        print(result)

if __name__ == '__main__':
    control = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }

    wrongreqd = {
            "host": 28,
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }

    wrongopt = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": "68",
            "policy": "AutoAdd"
            }

    missingreqd = {
            "host": "me",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }

    missingopt = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "policy": "AutoAdd"
            }

    blankopt = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": "",
            "policy": "AutoAdd"
            }

    blankreqd = {
            "host": "",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoAdd"
            }

    wrongpolicy = {
            "host": "me",
            "user": "admin",
            "passwd": "badpassword",
            "cmdlist": "la la la la la",
            "port": 68,
            "policy": "AutoBAD"
            }

    empty = {}

    testcases = {
                "control": control,
                "wrongreqd": wrongreqd, 
                "wrongopt": wrongopt, 
                "missingreqd": missingreqd, 
                "missingopt": missingopt, 
                "blankreqd": blankreqd, 
                "blankopt": blankopt, 
                "wrongpolicy": wrongpolicy,
                "empty": empty
                }

    sim = usersim.UserSim(True)
    for configName, config in testcases.items():
        print("Testing input: " + configName)
        run_test(sim, config)
