# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import tasks.test


class TestStopFail(tasks.test.Test):
    """ Task for testing when the stop method raises an exception.
    """
    def stop(self):
        raise Exception('Test exception raised.')
