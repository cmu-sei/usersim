from tasks import test


class TestConfig(test.Test):
    @classmethod
    def parameters(cls):
        """ Parameters to test.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
            containing the required and optional parameters of the class as keys and human-readable (str) descriptions
            and requirements for each key as values.
        """
        required = {'someint': 'any int value', 'somestr': 'any string',
                    'somefloat': 'a float'}
        optional = dict()

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
        assert isinstance(config, dict)

        for key in cls.parameters()['required']:
            if key not in config:
                raise KeyError(key)

        someint = config['someint']
        try:
            someint = int(someint)
        except ValueError:
            raise ValueError('someint: {} Should be able to be converted to an int.'.format(str(someint)))

        somestr = config['somestr']
        try:
            someint = str(somestr)
        except ValueError:
            raise ValueError('somestr: {} Should be able to convert to str.'.format(str(somestr)))

        somefloat = config['somefloat']
        try:
            somefloat = float(somefloat)
        except ValueError:
            raise ValueError('somefloat: {} Should be able to convert to a float'.format(str(somefloat)))

        return {'someint': someint, 'somestr': somestr, 'somefloat': somefloat}
