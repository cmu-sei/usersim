# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

from . import environment, guestinfo


cache = {}

def lookup(var_name):
    """ Try looking up an external variable.

    Args:
        var_name (str): Name of the variable to search for.

    Returns:
        str: The output of the lookup. Empty string if nothing was found.
    """
    value = cache.get(var_name, '')
    if not value:
        value = environment.lookup(var_name)
    if not value:
        value = guestinfo.lookup(var_name)

    cache[var_name] = value
    return value
