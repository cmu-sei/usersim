import tasks.test


class TestCleanupFail(tasks.test.Test):
    def cleanup(self):
        raise Exception('Test exception raised.')
