import tasks.test


class TestFeedback(tasks.test.Test):
    def __call__(self):
        super().__call__()
        raise Exception('Test exception raised.')
