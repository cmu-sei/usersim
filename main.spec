# -*- mode: python -*-
import datetime
import os
import re
import zipfile

block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['hooks/'],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='UserSimulator',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='UserSimulator')
timestamp = datetime.datetime.now().isoformat()[:-10]
timestamp = re.sub(':', '-', timestamp)
zipper = zipfile.ZipFile(coll.name + timestamp + '.zip', 'w')
rel_path = os.path.join(coll.name, '..')

for root, dirs, files in os.walk(coll.name):
    for file_ in files:
        abs_path = os.path.join(root, file_)
        zipper.write(abs_path, os.path.relpath(abs_path, rel_path), zipfile.ZIP_DEFLATED)
zipper.writestr(os.path.join(os.path.basename(coll.name), 'version.txt'), timestamp, zipfile.ZIP_DEFLATED)
zipper.close()
