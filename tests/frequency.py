import importlib

import api
import usersim


def run_test():
    reps = 10
    config = {'type': 'frequency',
              'config': {'frequency': 2000,
                         'repetitions': reps,
                         'task': {'type': 'test',
                                  'config': {}}}}

    importlib.reload(usersim)
    sim = usersim.UserSim()

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
