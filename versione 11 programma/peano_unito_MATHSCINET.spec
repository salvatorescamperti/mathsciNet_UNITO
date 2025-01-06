import sys ; sys.setrecursionlimit(sys.getrecursionlimit() * 5)
# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['C:\\Users\\scamp\\Desktop\\tortoise\\mathsciNet_UNITO\\versione 10 programma\\peano_unito_MATHSCINET.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='peano_unito_MATHSCINET',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\scamp\\Desktop\\tortoise\\mathsciNet_UNITO\\versionfile.txt',
    icon=['C:\\Users\\scamp\\Desktop\\tortoise\\mathsciNet_UNITO\\versione 10 programma\\risorse\\window_logo.ico'],
)
