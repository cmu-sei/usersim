import tasks


class TestNoStop(tasks.test.Test):
    def stop(self):
        super().stop()
        return False
