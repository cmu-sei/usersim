import tests
import traceback


def run_all_tests():
    successes = list()
    failures = list()

    for test in tests.loaded:
        try:
            test.run_test()
        except Exception:
            failures.append(test)
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

if __name__ == '__main__':
    run_all_tests()
