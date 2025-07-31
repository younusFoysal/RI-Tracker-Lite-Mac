# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('dist', 'dist')],
    hiddenimports=[
        'requests', 'urllib3', 'chardet', 'certifi', 'idna',  # requests and its dependencies
        'psutil',
        'pynput', 'pynput.keyboard', 'pynput.mouse',  # pynput and its modules
        'mss', 'mss.tools',
        'screeninfo',
        'webview', 'webview.platforms.winforms',  # webview and Windows-specific platform
        'sqlite3',
        'json', 'threading', 'subprocess', 'platform', 'shutil', 'random', 'tempfile', 'base64',
        'glob', 're', 'pathlib', 'datetime',
    ],
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
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
)
