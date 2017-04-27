### Hooks script for PyInstaller to correctly package all modules.
### PyInstaller must be run with the --additional-hooks-dir option.
import os


modules = [f for f in os.listdir('behaviors') if f[-3:] == '.py']

hiddenimports = ['behaviors.' + f[:-3] for f in modules if f != '__init__.py']
datas = [('behaviors' + os.sep + f, 'behaviors') for f in modules]
