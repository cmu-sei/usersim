import json
import traceback
import xml.etree as xmltree

import yaml


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
        list of dicts: The YAML document converted to Python objects.
            YAML constructs will be converted to Python objects by this conversion:
                Blank scalars become empty dicts
                All other scalars become strs
                Sequences become lists
                Mappings become dicts
    """
    def string_constructor(loader, node):
        return node.value

    def dict_constructor(loader, node):
        return dict()

    # For whatever reason, shorthand tags do not work.
    yaml_2002_prefix = 'tag:yaml.org,2002:'
    yaml_tags = ['bool',
                 'int',
                 'float',
                 'binary',
                 'timestamp']

    # Leaving commented for now, but may make a return if it's useful.
    #for tag in yaml_tags:
    #    yaml.add_constructor(yaml_2002_prefix + tag, string_constructor)
    yaml.add_constructor(yaml_2002_prefix + 'timestamp', string_constructor)

    yaml.add_constructor(yaml_2002_prefix + 'null', dict_constructor)

    return yaml.load(yaml_string)

def string_to_python(config_string):
    """ Converts a string in a supported language format to a list of dicts.

    Arguments:
        config_string (str): A string configuration in one of the supported formats (YAML, JSON, XML).
            This string should represent a list of dictionaries, each with the keys 'type' and 'config'.
            In YAML, the first document should be a sequence of mapping nodes.

    Returns:
        list of dicts: A Python list which includes any number of task configuration dictionaries, each with the keys
            'type' and 'config'.

    Raises:
        ValueError: If the given config_string does not meet its requirements.
    """
    try:
        structure = yaml_to_python(config_string)
    except Exception as e:
        raise ValueError('Input was not valid YAML.\n' + traceback.format_exc())
    else:
        if not isinstance(structure, list):
            raise ValueError('Invalid configuration - a list could not be inferred.')
        for task in structure:
            if not isinstance(task, dict):
                raise ValueError('Invalid configuration - a list item is empty.')
            if 'type' not in task:
                raise ValueError('Invalid configuration - a task is missing a type.')
            if 'config' not in task:
                raise ValueError('Invalid configuration - a task is missing its configuration.')
        return structure
