# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import tasks.test


class TestInitFail(tasks.test.Test):
    """ Task for testing when an exception is raised within __init__.
    """
    def __init__(self, config):
        super().__init__(config)
        raise Exception('Test exception raised.')
