# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import api
import usersim


def run_test():
    seconds = 10
    task = {'type': 'test', 'config': {}}

    config = {'type': 'delay',
              'config': {'task': task,
                         'seconds': seconds}}

    sim = usersim.UserSim(True)

    task_id = api.new_task(config)

    while True:
        sim.cycle()
        if api.status_task(2)['state'] == api.States.STOPPED:
            print('Nested delay task complete.')
            break

if __name__ == '__main__':
    run_test()
