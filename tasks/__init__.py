# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import importlib
import inspect
import os
import sys


__all__ = []
loaded = []
task_dict = {}

py_files = os.listdir(os.path.dirname(__file__))
special_modules = ['__init__.py', 'task.py']

def get_matching_class(module_name, loaded_module):
    for class_name, class_obj in inspect.getmembers(loaded_module, inspect.isclass):
        if class_name.lower() == module_name:
            return class_obj
    raise AttributeError('Could not find a matching class.')

def load_modules():
    global __all__
    global loaded
    global task_dict

    for candidate in py_files:
        module_name = candidate[:-3]
        if candidate in special_modules or candidate[-3:] != '.py':
            continue
        module = 'tasks.' + module_name
        try:
            loaded_module = importlib.import_module(module)
            class_obj = get_matching_class(module_name, loaded_module)
        except ImportError:
            print('Could not load module %s' % module)
            continue
        except AttributeError:
            print('Could not load a class in module %s matching the module name.' % module_name)
            continue
        else:
            print('Loaded module %s' % module)
            __all__.append(module_name)
            loaded.append(loaded_module)
            task_dict[module_name] = class_obj

load_modules()


# Avoid having a bunch of junk left over.
del py_files
del special_modules
