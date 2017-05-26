from tasks import task


class Test(task.Task):
    def __init__(self):
        print('%s task initialized.' % self.__class__)

    def __call__(self):
        print('%s task called.' % self.__class__)

    def cleanup(self):
        print('%s task cleanup called.' % self.__class__)
        pass

    def stop(self):
        print('%s task stop check called.' % self.__class__)
        return True

    def status(self):
        return '%s status.' % self.__class__

    @classmethod
    def config(cls, conf_dict):
        print('%s config class method called.' % cls)
        return cls()
