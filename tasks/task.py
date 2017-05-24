class Task(object):
    """ All methods must be overridden by subclasses.
    """
    def __init__(self):
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

    @classmethod
    def config(cls, conf_dict):
        """ Converts a configuration into an actual Task object.

        Args:
            conf_dict (dict): A dictionary of the configuration options for this class.

        Raises:
            KeyError: If a configuration option is missing.
            ValueError: If a configuration's value is not valid.

        Returns:
            Task: A configured Task object.
        """
        raise NotImplementedError("Not yet implemented.")
