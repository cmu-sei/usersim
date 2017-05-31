import importlib
import inspect
import os
import sys


__all__ = list()
loaded = list()

py_files = os.listdir(os.path.dirname(__file__))
special_modules = ['__init__.py']

def load_modules():
    global __all__
    global loaded

    for candidate in py_files:
        module_name = candidate[:-3]
        if candidate in special_modules or candidate[-3:] != '.py':
            continue
        module = 'tests.' + module_name
        try:
            loaded_module = importlib.import_module(module)
        except ImportError:
            print('Could not load test %s' % module)
            continue
        else:
            print('Loaded test %s' % module)
            __all__.append(module_name)
            loaded.append(loaded_module)

load_modules()


# Avoid having a bunch of junk left over.
del py_files
del special_modules


# Importable test runner.
def run_all_tests():
    successes = list()
    failures = list()

    for test in loaded:
        try:
            test.run_test()
        except Exception:
            failures.append((test, traceback.format_exc()))
        else:
            successes.append(test)

    print('********************************************************************************')
    print('********************************************************************************')
    print('********************************************************************************')
    if successes:
        print('The following tests passed:')
        for test in successes:
            print('    ' + str(test))
    else:
        print('NO TESTS PASSED.')
    print('********************************************************************************')
    print('********************************************************************************')
    print('********************************************************************************')
    if failures:
        print('The following tests failed:')
        for test in failures:
            print('    ' + str(test))
    else:
        print('ALL TESTS PASSED.')
