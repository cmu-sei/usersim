### Hooks script for PyInstaller to correctly package all modules.
### PyInstaller must be run with the --additional-hooks-dir option.

datas = [('geckodriver/geckodriver' + ext, 'geckodriver') for ext in (str(), '.exe')]
