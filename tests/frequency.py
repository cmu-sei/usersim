import importlib

import api
import usersim


def run_test():
    config = {'type': 'frequency',
              'config': {'frequency': 2000,
                         'repetitions': 10,
                         'task': {'type': 'test',
                                  'config': {}}}}

    importlib.reload(usersim)
    sim = usersim.UserSim()

    api.new_task(config)

    while True:
        result = sim.cycle()

        if len(result) > 1:
            print(result)

        if api.status_task(1)['state'] == api.States.STOPPED:
            break

if __name__ == '__main__':
    run_test()
