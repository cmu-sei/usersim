### Hooks script for PyInstaller to correctly package all modules.
### PyInstaller must be run with the --additional-hooks-dir option.
import os


modules = [f for f in os.listdir('tests') if f[-3:] == '.py']

hiddenimports = ['tests.' + f[:-3] for f in modules if f != '__init__.py']
datas = [('tests' + os.sep + f, 'tests') for f in modules]
