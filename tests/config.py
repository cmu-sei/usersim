import api
import config
import usersim


def test_xml():
    pass

def test_json():
    pass

def test_yaml():
    yaml_data = """
    - type: test
      config:
        someint: 42
        somestr: "blah"
        somefloat: 3.14159
    """
    print(yaml_data)
    structure = config.string_to_python(yaml_data)
    sim = usersim.UserSim(True)
    for task in structure:
        api.validate_config(task)

def run_test():
    test_yaml()

if __name__ == '__main__':
    run_test()
