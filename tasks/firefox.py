# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

import functools
import os
import platform
import queue
import random
import re
import sys
import threading
import time
import traceback

import psutil
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import api
from tasks import browser


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
    def get(cls, site, task_id, delay=0):
        """ Adds the _get() action to the queue. This method is required in order to avoid driver initialization sync
        issues.

        Args:
            site (str): URL to visit.
        """
        cls._add_action(functools.partial(cls._driver.get, site), task_id, delay)

    @classmethod
    def status(cls):
        return cls._status()

    @classmethod
    def _action_executor(cls):
        """ Services actions in the queue, which are functools.partial objects.
        """
        while True:
            action, task_id, delay = cls._action_queue.get()

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

            time.sleep(delay)

    @classmethod
    def _add_action(cls, partial_function, task_id, delay):
        """ Adds actions to the queue.

        Args:
            partial_function (functools.partial): The action to be called from within the driver thread.
        """
        cls._action_queue.put((partial_function, task_id, delay))

    @classmethod
    def _make_driver(cls):
        """ Creates Mozilla driver (geckodriver) based on operating system.
        """
        if not cls._driver:
            # Originally used os.getcwd(), but that fails when the program's working directory is anything but the
            # usersim root (such as when XGA starts it).
            usersim_path = os.path.dirname(sys.argv[0])
            gecko_loc = os.path.join(usersim_path, 'geckodriver', 'geckodriver')

            if platform.system() == 'Windows':
                gecko_loc += '.exe'

            try:
                cls._driver = webdriver.Firefox(executable_path=gecko_loc, log_path=os.devnull)
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


class Firefox(browser.Browser):
    """ Connects to specified websites using Firefox. Subsequent website visits will use the same window and tab.
    """
    def __init__(self, config):
        super().__init__(config)
        self._driver = SharedDriver()
