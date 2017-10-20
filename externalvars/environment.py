import os


def lookup(var_name):
    return os.environ.get(var_name, '')
