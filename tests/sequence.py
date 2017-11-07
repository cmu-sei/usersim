# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import api
import usersim


def run_test():
    test_1 = {'type': 'test',
              'config': {}}
    test_2 = {'type': 'testfeedback',
              'config': {}}
    config = {'type': 'sequence',
              'config': {'tasks': [test_1, test_2]}}

    sim = usersim.UserSim(True)

    task_id = api.new_task(config)

    print('Cycle 1')
    sim.cycle()

    print(api.status_task(task_id))

    print('Cycle 2')
    sim.cycle()

    print(api.status_task(task_id))

    print('Cycle 3')
    sim.cycle()

    # The sequence task may be stopped here, if it goes after the testfeedback task.
    print(api.status_task(task_id))

    print('Cycle 4')
    sim.cycle()

    # Otherwise it would be stopped here.
    print(api.status_task(task_id))


if __name__ == '__main__':
    run_test()
