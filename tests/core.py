import importlib

import api
import tasks
import usersim


def test_new_task():
    importlib.reload(usersim)
    task = {'type': 'test', 'config': {}}
    assert api.new_task(task) == 1

def test_new_task_stop():
    importlib.reload(usersim)
    task = {'type': 'testnostop', 'config': {}}
    assert api.new_task(task) == 1

def test_cycle():
    test_new_task()
    sim = usersim.UserSim()
    # First cycle should not have had any scheduled tasks to run yet - they will be scheduled at the end.
    assert not sim.cycle()
    # This cycle SHOULD have a feedback tuple.
    assert sim.cycle()

def test_scheduling_auto_stop():
    test_new_task()
    sim = usersim.UserSim()

    assert api.status_all()
    assert api.status_task(1)['state'] == api.States.TO_SCHEDULE

    sim.cycle()
    assert api.status_all()
    assert api.status_task(1)['state'] == api.States.SCHEDULED

    sim.cycle()
    assert not api.status_all()
    assert api.status_task(1)['state'] == api.States.STOPPED

    assert api.status_task(2)['state'] == api.States.UNKNOWN

def test_scheduling():
    test_new_task_stop()
    sim = usersim.UserSim()

    assert api.status_task(1)['state'] == api.States.TO_SCHEDULE
    sim.cycle()
    assert api.status_task(1)['state'] == api.States.SCHEDULED

    sim.cycle()
    assert api.status_task(1)['state'] == api.States.SCHEDULED

    api.pause_all()
    assert api.status_task(1)['state'] == api.States.TO_PAUSE

    # pauses should be idempotent
    api.pause_task(1)
    assert api.status_task(1)['state'] == api.States.TO_PAUSE

    sim.cycle()
    assert api.status_task(1)['state'] == api.States.PAUSED

    api.unpause_all()
    assert api.status_task(1)['state'] == api.States.TO_SCHEDULE

    # unpauses should be idempotent
    api.unpause_task(1)
    assert api.status_task(1)['state'] == api.States.TO_SCHEDULE

    sim.cycle()
    assert api.status_task(1)['state'] == api.States.SCHEDULED

    api.stop_all()
    assert api.status_task(1)['state'] == api.States.TO_STOP

    # stops should be idempotent
    api.stop_task(1)
    assert api.status_task(1)['state'] == api.States.TO_STOP

    sim.cycle()
    assert api.status_task(1)['state'] == api.States.STOPPED

def run_test():
    test_new_task()

    test_cycle()

    test_scheduling_auto_stop()

    test_scheduling()

if __name__ == '__main__':
    run_test()
