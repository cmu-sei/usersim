import importlib

import api
import tasks
import usersim


def test_new_task():
    importlib.reload(usersim)
    sim = usersim.UserSim()
    task = tasks.printstuff.PrintStuff.config(dict())
    assert sim.new_task(task) == 1

def test_cycle():
    test_new_task()
    sim = usersim.UserSim()
    # First cycle should not have had any scheduled tasks to run yet - they will be scheduled at the end.
    assert not sim.cycle()
    # This cycle SHOULD have a feedback tuple.
    assert bool(sim.cycle())

def test_scheduling():
    test_new_task()
    sim = usersim.UserSim()

    assert sim.status_all()
    assert sim.status_task(1)['state'] == api.States.TO_SCHEDULE

    sim.cycle()
    assert sim.status_all()
    assert sim.status_task(1)['state'] == api.States.SCHEDULED

    sim.cycle()
    assert not sim.status_all()
    assert sim.status_task(1)['state'] == api.States.STOPPED

if __name__ == '__main__':
    print('Running test_new_task')
    test_new_task()

    print('Running test_cycle')
    test_cycle()

    print('Running test_scheduling')
    test_scheduling()
