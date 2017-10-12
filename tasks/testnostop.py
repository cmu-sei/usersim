import tasks.test


class TestNoStop(tasks.test.Test):
    """ Task for testing when a task's stop method returns False.
    """
    def stop(self):
        super().stop()
        return False
