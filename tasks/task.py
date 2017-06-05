class Task(object):
    #might need paramiko


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


        like startaction
        """
        raise NotImplementedError("Not yet implemented.")

    def cleanup(self):
        """ Called in the event __call__ raises an exception or when the stop method returns True. This method should
        never raise an exception. Use this method to handle cleaning up any open handles, files, or whatever needs to be
        closed in order to free up the memory that this object is using. This method must be overridden, but it is fine
        for it not to actually do anything if that is intended functionality.

        override and pass
        """
        raise NotImplementedError("Not yet implemented.")

    def stop(self):
        """ Each time the task runs, the scheduler subsequently calls this method to check if the Task object
        should be descheduled.

        Returns:
            bool: True if this object should be descheduled. False if it should stay in the scheduler.



        probably just return true
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
            conf_dict (dict): The dictionary to validate. Its keys and values are subclass-specific.

        Raises:
            KeyError: If a required configuration option is missing. The error message is the missing key.
            ValueError: If a configuration option's value is not valid. The error message is in the following format:
                key: value requirement


        Returns:
            dict: The dict given as the conf_dict argument with missing optional parameters added with default values.
        """
        

        params = cls.parameters()
        reqd_vparams = {}
        opt_vparams = {}
        for item in params["required"]:
            reqd_vparams[item] = item.value.split(":", 1)[0]
        for item in params["optional"]:
            opt_vparams[item] = [item.value.split(":", 1)[0], item.value.split("Default: ", 1)[1]]

        #1. check for KeyErrors (missing required parameters)
        for item in params_reqd.keys:
            if item not in conf_dict.keys
                raise KeyError(item)

        #2. check for ValueError (all keys present, but some keys have incorrect values)
        else:
            for item in conf_dict:

                #check if item is a required parameter
                if item in params_reqd: 
                    if type(item.value).__name__ not in params_reqd[item].value or not item.value:
                        raise ValueError(item + ": " + item.value)

                #otherwise item is an optional parameter
                else: 
                    #if the item doesn't have a value, we can just put in the default value
                    if not item.value:
                        item.value = params_opt[item].value[1]
                    #otherwise if the type is wrong we can raise a ValueError
                    else if type(item.value).__name__ not in params_opt[item].value:
                        raise ValueError(item + ": " + item.value)

        #3. put in default values for any missing optional parameters
        for item in params_opt:
            if item not in conf_dict:
                conf_dict[item] = params_opt[item].value[1]
        

