import itertools
import sys
import time
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

    spinner = itertools.cycle('-/|\\')
    while True:
        result = sim.cycle()
        for feedback in result:
            feedback_queue.put(feedback)

        # Spinner to demonstrate that the simulator is still running without scrolling the terminal.
        for i in range(4):
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(.25)
            sys.stdout.write('\b')

if __name__ == '__main__':
    main()
