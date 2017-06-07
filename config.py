import json
import xml.etree as xmltree
import yaml


def json_to_python(json_string):
    """ Converts a JSON configuration to a list of dicts.
    """
    return json.loads(json_string)

def xml_to_python(xml_string):
    """ Converts an XML configuration to a list of dicts.
    """
    raise NotImplementedError('XML configuration not yet implemented.')

def yaml_to_python(yaml_string):
    """ Converts a YAML configuration to a list of dicts.

    Arguments:
        yaml_string (str): A string containing a YAML document which consists of a list of dictionaries.
            Example:
                - type: test
                  config:

                - type: attime
                  config:
                      time: 2345
                      task:
                          type: test
                          config:

    Returns:
        list of dicts: The YAML document converted to Python objects, which will be a list of dicts.
            YAML constructs will be converted to Python objects by this conversion:
                None from -, null
                bool from true, false, on, and off
                int from 42
                float from 3.14159
                list from [1, 2.0, 'three'] or when - list notation is used
                dict from {one: 1, two: 2}
    """
    return yaml.load(yaml_string)

def string_to_python(config_string):
    """ Converts a string in a supported language format to a list of dicts.
    """
    converters = [json_to_python,
                  xml_to_python,
                  yaml_to_python]

    structure = None

    for converter in converters:
        try:
            structure = converter(config_string)
        except Exception:
            continue

    if structure:
        return structure
    else:
        raise ValueError('Could not determine a valid structure from the given configuration string:\n' + config_string)
