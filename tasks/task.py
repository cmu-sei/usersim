class Task(object):
    """ The highest common ancestor for all other tasks.
    """
    def __init__(self, config):
        raise NotImplementedError('Not yet implemented.')

    def __call__(self):
        """ Periodically called while the object is scheduled. This gives the object its behavior, whatever that may
        entail.
        """
        raise NotImplementedError('Not yet implemented.')

    def cleanup(self):
        """ Called when the stop method returns True. Use this method to handle cleaning up any open handles, files, or
        whatever needs to be closed in order to free up the memory that this object is using. This method must be
        overridden, but it is fine for it not to actually do anything if that is intended functionality.
        """
        raise NotImplementedError('Not yet implemented.')

    def stop(self):
        """ Each time the task runs, the scheduler subsequently calls this method to check if the Task object
        should be descheduled.

        Returns:
            bool: True if this object should be descheduled. False if it should stay in the scheduler.
        """
        raise NotImplementedError('Not yet implemented.')

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        raise NotImplementedError('Not yet implemented.')

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and a string formatted as follows:
                'type: human-readable description' where type can be any of the following strings: 'str', 'int',
                'float', 'bool', 'any', or 'task', or any of these types may be encased in [square] or {curly} brackets
                to indicate a list or dict, respectively. Such a dict object must include both key and value types,
                like so: {str: int}. The space is important to the parser.
                These types may be nested together to form any list or dict nested structure, such as a list of lists.
        """
        raise NotImplementedError('Not yet implemented.')

    @classmethod
    def validate(cls, config):
        """ Validates the given configuration dictionary.

        Args:
            config (dict): The dictionary to validate. Its keys and values are subclass-specific.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the config argument with missing optional parameters added with default values.
        """
        raise NotImplementedError('Not yet implemented.')
