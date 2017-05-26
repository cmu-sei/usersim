import traceback

import api
import tasks
import usersim


def main():
    conf_dict = {'type': 'frequency',
                 'config': {'frequency': 720,
                            'repetitions': 10,
                            'task': {'type': 'test',
                                     'config': {}}}}

    sim = usersim.UserSim()
    api.new_task(conf_dict)

    while True:
        result = sim.cycle()
        if len(result) > 1:
            print(result)

if __name__ == '__main__':
    main()
