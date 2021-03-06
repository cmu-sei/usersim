# Copyright 2017 Carnegie Mellon University. See LICENSE.md file for terms.

# Hook script for Firefox task to package the required geckodriver.
import platform


geckodriver_path = 'geckodriver/geckodriver'
if platform.system() == 'Windows':
    geckodriver_path += '.exe'
datas = [(geckodriver_path, 'geckodriver')]
