import os
import importlib

__all__ = list()
loaded = list()

py_files = os.listdir(os.path.dirname(__file__))

for candidate in py_files:
    if candidate == '__init__.py' or candidate[-3:] != '.py':
        continue
    module = 'tasks.' + candidate[:-3]
    try:
        loaded_module = importlib.import_module(module)
    except ImportError:
        print('Could not load module %s' % module)
        continue
    else:
        print('Loaded module %s' % module)
        __all__.append(candidate[:-3])
        loaded.append(loaded_module)
del module
del candidate
del py_files
