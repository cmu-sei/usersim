import traceback

import tasks


def main():

    conf_dict = {'type': 'frequency',
                 'config': {'frequency': 720,
                            'repetitions': 10,
                            'behavior': {'type': 'printstuff',
                                         'config': {}}}}

    behavior_set = set()

    new_behavior = tasks.task_dict[conf_dict['type']].config(conf_dict['config'])
    behavior_set.add(new_behavior)

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
                        behavior_obj = tasks.task_dict[result['type']].config(result['config'])
                    except KeyError as e:
                        print(e)
                    except ValueError as e:
                        print(e)
                    else:
                        new_behaviors.add(behavior_obj)

        behavior_set |= new_behaviors
        behavior_set -= delete_behaviors

if __name__ == '__main__':
    main()
