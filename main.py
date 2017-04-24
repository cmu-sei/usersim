import traceback

import behaviors.frequency
import behaviors.printstuff
import behavior


def main():
    conf_dict = {'type': 'frequency',
                 'config': {'frequency': 720,
                            'repetitions': 10,
                            'behavior': {'type': 'printstuff',
                                         'config': {}}}}

    behavior_set = set()
    behavior_set.add(behaviors.frequency.Frequency.config(conf_dict['config']))

    while behavior_set:
        new_behaviors = set()
        delete_behaviors = set()

        for task in behavior_set:
            try:
                result = task()
            except Exception:
                print(traceback.format_exc())
            else:
                if result is None:
                    if task.stop():
                        task.cleanup()
                        delete_behaviors.add(task)
                else:
                    try:
                        behavior_obj = behaviors.printstuff.PrintStuff.config(result['config'])
                    except KeyError as e:
                        print(e)
                    except ValueError as e:
                        print(e)
                    else:
                        new_behaviors.add(behavior_obj)

        #behavior_set = behavior_set | new_behaviors - delete_behaviors
        behavior_set |= new_behaviors
        behavior_set -= delete_behaviors

if __name__ == '__main__':
    main()
