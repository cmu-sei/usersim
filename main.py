import api
import tasks
import usersim
import tests


def main():
    conf_dict = {'type': 'frequency',
                 'config': {'frequency': 720,
                            'repetitions': 10,
                            'task': {'type': 'test',
                                     'config': {}}}}
    api.new_task(conf_dict)

    sim = usersim.UserSim()
    while True:
        result = sim.cycle()
        if result:
            print(result)

if __name__ == '__main__':
    main()
