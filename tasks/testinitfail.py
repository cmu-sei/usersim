import tasks.test


class TestInitFail(tasks.test.Test):
    def __init__(self, config):
        super().__init__(config)
        raise Exception('Test exception raised.')
