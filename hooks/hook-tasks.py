### Hooks script for PyInstaller to correctly package all modules.
### PyInstaller must be run with the --additional-hooks-dir option.
import os


modules = [f for f in os.listdir('tasks') if f[-3:] == '.py']

hiddenimports = ['tasks.' + f[:-3] for f in modules if f != '__init__.py']
datas = [('tasks' + os.sep + f, 'tasks') for f in modules]
