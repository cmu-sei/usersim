import behavior

class PrintStuff(behavior.Behavior):
    def __init__(self):
        pass

    def __call__(self):
        print('Printed stuff')

    def cleanup(self):
        pass

    def stop(self):
        return True

    @classmethod
    def config(cls, conf_dict):
        return cls()
