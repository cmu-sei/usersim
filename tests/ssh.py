import api



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


    testcases = {
                "good": good,
                "wrongreqd": wrongreqd, 
                "wrongopt": wrongopt, 
                "missingreqd": missingreqd, 
                "missingopt": missingopt, 
                "blankreqd": blankreqd, 
                "blankopt": blankopt, 
                "wrongpolicy": wrongpolicy
                }

    sim = usersim.UserSim(True)
    for item in testcases:
        print("Testing input: " + item.key)
        run_test(sim, item.value)
