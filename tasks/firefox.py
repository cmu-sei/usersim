import functools
import os
import platform
import queue
import random
import re
import threading
import traceback

import psutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import api
from tasks import task


class SharedDriver(object):
    """ SharedDriver allows all Firefox tasks to use the same browser window and tab. Tasks executed by SharedDriver are
    added to a queue which is serviced by a threaded loop.
    """
    _driver = None
    _action_queue = None

    def __new__(cls):
        """ Creates a new instance only if _action_queue does not already exist. Starts the threaded action_executor
        which perpetually listens for new actions to execute.
        """
        if not cls._action_queue:
            cls._action_queue = queue.Queue()
            cls._make_driver()

            t = threading.Thread(target=cls._action_executor)
            t.daemon = True
            t.start()

        return cls

    @classmethod
    def get(cls, site, task_id):
        """ Adds the _get() action to the queue. This method is required in order to avoid driver initialization sync
        issues.

        Args:
            site (str): URL to visit.
        """
        cls._add_action(functools.partial(cls._driver.get, site), task_id)

    @classmethod
    def _action_executor(cls):
        """ Services actions in the queue, which are functools.partial objects.
        """
        while True:
            action_details = cls._action_queue.get()
            action = action_details[0]
            task_id = action_details[1]

            try:
                title = cls._driver.title
            except WebDriverException as e:
                cls._driver = None
                cls._make_driver()
                cls._add_action(action, task_id)

            try:
                action()
            except Exception:
                api.add_feedback(task_id, traceback.format_exc())

    @classmethod
    def _add_action(cls, partial_function, task_id):
        """ Adds actions to the queue.

        Args:
            partial_function (functools.partial): The action to be called from within the driver thread.
        """
        cls._action_queue.put((partial_function, task_id))

    @classmethod
    def _make_driver(cls):
        """ Creates Mozilla driver (geckodriver) based on operating system.
        """
        if not cls._driver:
            gecko_loc = os.path.join(os.getcwd(), 'geckodriver', 'geckodriver')

            if platform.system() == 'Windows':
                gecko_loc += '.exe'

            try:
                cls._driver = webdriver.Firefox(executable_path=gecko_loc)
            except WebDriverException:
                # First, close the browser window that may have opened as a result of that call.
                for process in psutil.process_iter():
                    if 'firefox' in process.name():
                        process.kill()

                # Then switch to the old protocol for Firefox versions earlier than 48.
                dc = DesiredCapabilities.FIREFOX
                dc['marionette'] = False

                try:
                    cls._driver = webdriver.Firefox(capabilities=dc)
                except WebDriverException:
                    # If it failed that time, kill the window and just raise the exception.
                    for process in psutil.process_iter():
                        if 'firefox' in process.name():
                            process.kill()
                    raise

            # This does not work correclty with Selenium 3.3 with geckodriver 0.15.0. It works with Selenium 3.0.2 with
            # geckodriver 0.14.0. Newer versions than 3.3/0.15.0 have not yet been tested.
            cls._driver.set_page_load_timeout(5)

    @classmethod
    def _status(cls):
        """ Status message for activate driver.

        Returns:
            str: 'No active Firefox driver.' or 'Active Firefox driver.'.
        """
        if not cls._driver:
            return 'No active Firefox driver.'

        return 'Active Firefox driver.'


class Firefox(task.Task):
    """ Connects to specified websites using Firefox. Subsequent website visits will use the same window and tab.
    """
    def __init__(self, config):
        """ Validates config and stores it as an attribute. Determines and stores as an attribute the operating system
        of the system running UserSim.
        """
        self._sites = config['sites']

        self._driver = SharedDriver()

    def __call__(self):
        """ Creates a SharedDriver based on the operating system. Randomly chooses and visits one of the provided
        websites.
        """
        site_request = random.choice(self._sites)
        self._driver.get(site_request, self._task_id)

    def cleanup(self):
        """ Doesn't need to do anything.
        """
        pass

    def stop(self):
        """ This task should be stopped after running one.

        Returns:
            True
        """
        return True

    def status(self):
        """ Called when status is polled for this task.

        Returns:
            str: An arbitrary string giving more detailed, task-specific status for the given task.
        """
        return self._driver._status()

    @classmethod
    def parameters(cls):
        """ Returns a dictionary with the required and optional parameters of the class, with human-readable
        descriptions for each.

        Returns:
            dict of dicts: A dictionary whose keys are 'required' and 'optional', and whose values are dictionaries
                containing the required and optional parameters of the class as keys and human-readable (str)
                descriptions and requirements for each key as values.
        """
        params = {'required': {'sites': 'list: list of sites to connect to (must be FQDN).'
                                        ' One will be randomly chosen each time the module is run.'},
                  'optional': {}}

        return params

    @classmethod
    def validate(cls, conf_dict):
        """ Validates the given configuration dictionary.  Makes sure that config['required'] is a list of strings.
        Does not actually check if the strings are valid.

        Args:
            config (dict): The dictionary to validate. See parameters() for required format.

        Raises:
            KeyError: If a required configuration option is missing.  The error message relays the missing key.
            ValueError: If a configuration option's value is not valid.  The error message relays the proper format.
        """

        params = cls.parameters()
        required = params['required']

        for item in required:
            if item not in conf_dict:
                raise KeyError(item)

        site_list = conf_dict['sites']
        if not isinstance(site_list, list):
            raise ValueError('sites: {} Websites to visit must be a list of strings.'.format(str(site_list)))
        for site in site_list:
            if not isinstance(site, str):
                raise ValueError('sites: {} Listed website is not a string.'.format(str(site)))

        url_pattern = '^(http|https)://'
        for item in site_list:
            if not re.match(url_pattern, item):
                raise ValueError('Incorrect URL pattern: {} - must start with http:// or https://'.format(item))

        return conf_dict
