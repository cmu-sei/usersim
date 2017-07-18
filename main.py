import queue

import api
import cli
import tasks
import tests
import usersim


def main():
    feedback_queue = queue.Queue()

    test_mode = cli.parse_and_initialize(feedback_queue)

    if test_mode:
        tests.run_all_tests()
        return

    sim = usersim.UserSim()

    while True:
        result = sim.cycle()
        for feedback in result:
            feedback_queue.put(feedback)

if __name__ == '__main__':
    main()
