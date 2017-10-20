import json
import traceback
import xml.etree as xmltree

import yaml

import api


class TaskConfig(dict):
    """ Tasks are just a dict object with a particular structure, which must be evaluated in a particular way.
    This wrapper class is not actually instantiated - it's just used to distinguish a 'task' in a configuration as
    opposed to the more general dictionary. A task configuration can be processed with api.validate_config
    """
    pass

primitives = {'str': str,
              'int': int,
              'float': float,
              'bool': bool,
              'any': (str, int, float, bool),
              'number': (int, float),
              'task': TaskConfig}

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
        return {}

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

def parse_primitive(string):
    """ Check if a string matches a key in the primitives dict.

    Args:
        string (str): String to evaluate. Must be 'str', 'int', 'bool', 'float', 'any', 'number', or 'task'.

    Raises:
        ValueError: If string is not in the primitives dict.

    Returns:
        type or tuple: If string is 'str', 'int', 'bool', or 'float', returns the corresponding type's built-in. If
            string is 'any', returns a tuple containing all of the aforementioned types. If string is 'number',
            returns a tuple containing the int and float built-ints. If string is 'task', returns the TaskConfig class.
    """
    if string not in primitives:
        raise ValueError('{} is not a valid primitive type.'.format(string))

    return primitives[string]

def parse_collection(collection):
    """ Recursively process the collection based on its type.

    Args:
        collection (list or dict): Any list or dict object containing one entry. (one element in a list, one key:value
            pair in a dict)

    Raises:
        ValueError: If the given collection does not have exactly one entry.
        Exception: Any of the exceptions that may be raised by parse_list or parse_dict.

    Returns:
        list: If collection was a list.
        dict: If collection was a dict.
    """
    if not len(collection) == 1:
        raise ValueError('Given collection {} should have exactly ONE entry.'.format(list_))

    if isinstance(collection, list):
        return parse_list(collection)
    elif isinstance(collection, dict):
        return parse_dict(collection)

def parse_list(list_):
    """ Recursively process a list.

    Args:
        list_ (list): A list containing one element.

    Raises:
        Exception: Any exception that may be raised by parse_item.

    Returns:
        list: A list which may contain any type structure. It will have exactly one element.
    """
    item = list_.pop()

    return [parse_item(item)]

def parse_dict(dict_):
    """ Recursively process a dict.

    Args:
        dict_ (dict): A dict containing one key:value pair.

    Raises:
        Exception: Any exception that may be raised by parse_item.

    Returns:
        dict: A dict which may contain only primitives as a key, and any type structure as a value. It will have exactly
            one key:value pair.
    """
    key_type = next(iter(dict_))
    value_type = dict_[key_type]

    return {parse_item(key_type): parse_item(value_type)}

def parse_item(item):
    """ Recursively process an item.

    Args:
        item (str, list, or dict): If item is a str object, then it should match one of the keys in the primitives dict
            above. If it is a list or dict, it should have exactly one entry.

    Raises:
        ValueError: If item is not a str, list, or dict object.
        Exception: Any exception that may be raised by parse_primitive or parse_collection.
    """
    if isinstance(item, str):
        return parse_primitive(item)
    elif isinstance(item, (list, dict)):
        return parse_collection(item)
    else:
        raise ValueError('Got an item that is not a str, list, or dict object: {}'.format(item))

def type_check(config, type_tree):
    """ Recursively checks if the types in config match the types in type_tree.

    Args:
        config (int, bool, float, str, list, or dict): Any value is valid.
        type_tree (type, tuple, list, or dict): Essentially, can be any of the values of the primitives dict at the top
            of this file, or can be a list or dict object.

    Raises:
        ValueError: If there is a type mismatch between config and type_tree.

    Returns:
        int, bool, float, str, list, or dict: Returns config as it was except in the case where type_tree is the
            TaskConfig type. In that case, a dict is still returned, but it is first processed by api.validate_config.
    """
    if isinstance(config, list) and isinstance(type_tree, list):
        for item in config:
            type_check(item, next(iter(type_tree)))
        return config
    elif isinstance(config, dict) and isinstance(type_tree, dict):
        for key, value in config.items():
            key_type, value_type = next(iter(type_tree.items()))
            type_check(key, key_type)
            type_check(value, value_type)
        return config
    elif isinstance(config, dict) and type_tree is TaskConfig:
        # Then we need to use the API to validate it.
        return api.validate_config(config)

    # Basically, check if the types don't match. Obviously, if config is a list or dict and type_tree is NOT, it's safe
    # to say we have a type mismatch. Conversely, if type_tree is a list or dict and config is not, then we also have a
    # mismatch. Finally, we check if primitive types are mismatched. If any of these conditions are true, we raise.
    if isinstance(config, list) or isinstance(config, dict) or \
       isinstance(type_tree, list) or isinstance(type_tree, dict) or \
       not isinstance(config, type_tree):
        # config is not a list or dict after we've already checked those, and its type also doesn't match what it should
        # be, so raise an exception.
        type_ = type_tree if type_tree.__class__ == type else type_tree.__class__
        raise ValueError('{} was an incorrect type - it should have been a {}'.format(config, type_))

    # It was a valid type, so it should be returned.
    return config

def validate(config, required_, optional_, defaults):
    """ Validates that config contains the required keys, as well as ensures that types match the given required and
    optional parameters. Missing optional keys are added from defaults.

    Args:
        config (dict): A task configuration dictionary. This must contain all required keys and may contain optional
            keys.
        required_ (dict): A dict containing the task's required keys mapped to str values of the form
            'type: description', where type may be 'str', 'bool', 'int', 'float', 'any', 'task', or such a string may be
            nested within any number of [] or {}. The '|' character will be used to split, so it must be
            present in the value string.
        optional_ (dict): A dict containing the task's optional keys, otherwise identical to required_.
        defaults (dict): A dict whose keys match the keys in optional_, and whose values are considered sane defaults.

    Raises:
        KeyError: If a required key is missing. The exception message will be the missing key.
        Exception: Any of the exceptions that may be generated by parse_item, yaml.load, or type_check.

    Returns:
        dict: The config argument with missing optional keys filled in with values from the defaults dict.
    """
    required = {}
    optional = {}

    for key, value in required_.items():
        type_string = value.split('|', 1)[0].strip()
        type_tree = yaml.load(type_string)
        required[key] = parse_item(type_tree)

    for key, value in optional_.items():
        type_string = value.split('|', 1)[0].strip()
        type_tree = yaml.load(type_string)
        optional[key] = parse_item(type_tree)

    for key in required:
        if key not in config:
            raise KeyError(key)
        type_check(config[key], required[key])

    for key in optional:
        if key not in config:
            config[key] = defaults[key]
        type_check(config[key], optional[key])

    return config
