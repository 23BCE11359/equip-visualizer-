# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import PyQt5
import os

# Collect all PyQt5 and matplotlib submodules as hidden imports to be safe.
hiddenimports = collect_submodules('PyQt5') + collect_submodules('matplotlib')

# Manually gather Qt platform plugins (e.g., qwindows.dll) from PyQt5 install and add
# matplotlib data (fonts, mpl-data)
datas = collect_data_files('matplotlib')

# Platform plugins are typically in PyQt5/Qt/plugins/platforms
plugins_dir = os.path.join(os.path.dirname(PyQt5.__file__), 'Qt', 'plugins', 'platforms')
if os.path.isdir(plugins_dir):
    for fname in os.listdir(plugins_dir):
        src = os.path.join(plugins_dir, fname)
        # Install into PyQt5/Qt/plugins/platforms inside the bundle
        datas.append((src, os.path.join('PyQt5', 'Qt', 'plugins', 'platforms')))

# Analysis
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=['runtime-hook-qt.py'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='ChemicalVisualizer',
    debug=False,
    strip=False,
    upx=True,
    console=False,
)
