import datetime

import api
import config
import usersim


def test_xml():
    pass

def test_json():
    pass

def test_yaml():
    yaml_data = """
    - type: testconfig
      config:
        someint: 42
        somestr: "blah"
        somefloat: 3.14159
        somenumber: 5
        othernumber: 2.53
        somelist:
            - 3.5
    """
    structure = config.string_to_python(yaml_data)

    assert len(structure) == 1

    task_dict = structure[0]
    assert isinstance(task_dict, dict)

    data_dict = task_dict['config']
    assert isinstance(data_dict, dict)

    assert data_dict['someint'] == 42
    assert data_dict['somestr'] == 'blah'
    assert data_dict['somefloat'] == 3.14159
    assert data_dict['somenumber'] == 5
    assert data_dict['othernumber'] == 2.53

    for task in structure:
        api.validate_config(task)

def run_test():
    test_yaml()

if __name__ == '__main__':
    run_test()
