import queue

import api
from communication import local
import tasks
import tests
import usersim


def main():
    feedback_queue = queue.Queue()
    comm = local.LocalCommunication(feedback_queue, 'test.yaml')
    sim = usersim.UserSim()

    while True:
        result = sim.cycle()
        for feedback in result:
            feedback_queue.put(feedback)

if __name__ == '__main__':
    main()
