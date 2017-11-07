# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import api
import usersim


def run_test():
    reps = 10
    config = {'type': 'frequency',
              'config': {'frequency': 2000,
                         'repetitions': reps,
                         'task': {'type': 'test',
                                  'config': {}}}}

    sim = usersim.UserSim(True)

    task_id = api.new_task(config)

    while True:
        result = sim.cycle()

        if len(result) > 1:
            print(result)

        # Break once the final task has been stopped.
        if api.status_task(task_id + reps)['state'] == api.States.STOPPED:
            break

if __name__ == '__main__':
    run_test()
