from tasks import test

import api


class TestConfig(test.Test):
    @classmethod
    def parameters(cls):
        """ Parameters to test.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
            containing the required and optional parameters of the class as keys and human-readable (str) descriptions
            and requirements for each key as values.
        """
        required = {'someint': 'int: an int',
                    'somestr': 'str: a string',
                    'somefloat': 'float: a float'}
        optional = {'somedict': '{str: int}: a dict mapping str to int',
                    'somelist': '[float]: a list of floats'}

        return {'required': required, 'optional': optional}

    @classmethod
    def validate(cls, config):
        """ Test for the config component.

        Arguments:
            config (dict): The dictionary to validate.

        Raises:
            AssertionError: If config is not a dict.
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: if a configuration option's value is not valid. The error message is in the following format:
                key: value requirement
        """
        defaults = {'somedict': {'yay': 3},
                    'somelist': [3.14159]}
        return api.check_config(config, cls.parameters(), defaults)
