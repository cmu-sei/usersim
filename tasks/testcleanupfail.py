import tasks.test


class TestCleanupFail(tasks.test.Test):
    """ Test task for when the cleanup method raises an exception.
    """
    def cleanup(self):
        raise Exception('Test exception raised.')
