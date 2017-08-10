import tasks.test


class TestStopFail(tasks.test.Test):
    def stop(self):
        raise Exception('Test exception raised.')
