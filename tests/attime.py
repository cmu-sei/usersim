import datetime
import importlib

import api
import usersim


def run_test():
    # Calculate the trigger time to be 10 seconds from now.
    trigger_time = datetime.datetime.now() + datetime.timedelta(seconds=5)
    trigger_time = trigger_time.time()
    time = '{}{}'.format(str(trigger_time.hour), str(trigger_time.minute))
    seconds = float(trigger_time.second)
    print('Trigger time is {}'.format(str(trigger_time)))

    config = {'type': 'attime',
              'config': {'time': str(time),
                         'seconds': seconds,
                         'task': {'type': 'test',
                                  'config': {}}}}

    importlib.reload(usersim)
    sim = usersim.UserSim()

    task_id = api.new_task(config)
    sim.cycle()

    print(sim._scheduled[task_id]._trigger_time)

    while True:
        result = sim.cycle()

        if len(result) > 1:
            print(result)

        # Only break once we see the nested task has been stopped.
        if api.status_task(2)['state'] == api.States.STOPPED:
            break

if __name__ == '__main__':
    run_test()