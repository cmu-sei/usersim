# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import tasks.test


class TestNoStop(tasks.test.Test):
    """ Task for testing when a task's stop method returns False.
    """
    def stop(self):
        super().stop()
        return False
