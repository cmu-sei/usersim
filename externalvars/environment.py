# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import os


def lookup(var_name):
    return os.environ.get(var_name, '')
