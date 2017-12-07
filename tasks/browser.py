# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import random
import re

import api
from tasks import task

class SharedDriver(object):
    """ Base class for sharing a browser driver. Must be implemented in the actual browser task.
    """
    def __new__(cls):
        raise NotImplementedError

    def get(cls, site, task_id, delay=0):
        """
        """
        raise NotImplementedError

    def status():
        raise NotImplementedError

class Browser(task.Task):
    """ Base class for browser tasks. Has no inherent functionality without an implementation of SharedDriver.
    """
    def __init__(self, config):
        """ Subclasses must add self._driver = SharedDriver for their module's SharedDriver version.
        """
        self._sites = config['sites']
        self._sequential = config['sequential']
        self._delay = config['delay']
        # NOTE: self._driver = SharedDriver()

    def __call__(self):
        if self._sequential:
            for site in self._sites:
                self._driver.get(site, self._task_id, self._delay)
        else:
            self._driver.get(random.choice(self._sites), self._task_id, self._delay)

    def cleanup(self):
        pass

    def stop(self):
        return True

    def status(self):
        return self._driver.status()

    @classmethod
    def parameters(cls):
        params = {'required': {'sites': '[str]| List of sites to connect to. (Must be FQDN) '
                                        ' By default, one is chosen at random.'},
                  'optional': {'sequential': 'bool| True means browse to all given sites in order. False means '
                                             'pick one at random. Default is False.',
                               'delay': 'int| Delay to insert after each site. Usually used with sequential set to '
                                        'True, but that is not required. Must not be negative. Default is 0.'}}
        return params

    @classmethod
    def validate(cls, config, extra_defaults={}):
        """ All the standard functionality of validate, plus the addition of extra_defaults so subclasses can use
        the same code.
        """
        defaults = {'sequential': False, 'delay': 0}
        defaults.update(extra_defaults)
        config = api.check_config(config, cls.parameters(), defaults)

        site_list = config['sites']

        if not site_list:
            raise ValueError('sites: {} Must be non-empty.'.format(str(config['sites'])))

        # Intended to match http:// and https:// at the beginning of a URL.
        url_pattern = re.compile('^(http|https)://')
        for site in site_list:
            if not url_pattern.match(site):
                raise ValueError('Incorrect URL pattern: {} - must start with http:// or https://'.format(site))

        if config['delay'] < 0:
            raise ValueError('delay: {} Must not be negative.'.format(str(config['delay'])))

        return config
