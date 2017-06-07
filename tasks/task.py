class Task(object):
    """ All methods must be overridden by subclasses.
    """
    def __init__(self, config):
        raise NotImplementedError("Not yet implemented.")

    def __call__(self):
        """ Periodically called while the object is scheduled. This gives the object its behavior, whatever that may
        entail.

        Returns:
            dict or None: If this task wants another task to be scheduled, this call should return the
                configuration for that task as a dict. Otherwise, it should not return anything, which is equivalent
                to returning None.
        """
        raise NotImplementedError("Not yet implemented.")

    def cleanup(self):
        """ Called in the event __call__ raises an exception or when the stop method returns True. This method should
        never raise an exception. Use this method to handle cleaning up any open handles, files, or whatever needs to be
        closed in order to free up the memory that this object is using. This method must be overridden, but it is fine
        for it not to actually do anything if that is intended functionality.
        """
        raise NotImplementedError("Not yet implemented.")

    def stop(self):
        """ Each time the task runs, the scheduler subsequently calls this method to check if the Task object
        should be descheduled.

        Returns:
            bool: True if this object should be descheduled. False if it should stay in the scheduler.
        """
        raise NotImplementedError("Not yet implemented.")

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        raise NotImplementedError("Not yet implemented.")

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        raise NotImplementedError("Not yet implemented.")

    @classmethod
    def validate(cls, conf_dict):
        """ Validates the given configuration dictionary.

        Args:
            conf_dict (dict): The dictionary to validate. Its keys and values are subclass-specific. Its values should
                be assumed to be str type and converted appropriately.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement

        Returns:
            dict: The dict given as the conf_dict argument with missing optional parameters added with default values.
        """
        raise NotImplementedError("Not yet implemented.")
