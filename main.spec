# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

playwright_datas, playwright_binaries, playwright_hiddenimports = collect_all('playwright')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=playwright_binaries,
    datas=[
        ('campus_wifi.png', '.'),
        ('profiles', 'profiles'),
    ] + playwright_datas,
    hiddenimports=[
        'plyer.platforms.win.notification',
        'plyer.platforms.win',
        'plyer',
        'tkinter',
        'tkinter.ttk',
        'pystray',
        'PIL',
        'requests',
        'core.strategies.playwright_strategy',
        'core.strategies.http_strategy',
        'core.strategies.factory',
        'core.profile_manager',
        'core.credential_manager',
        'core.state_manager',
        'ui.dashboard',
    ] + playwright_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CampusWiFiAssistant',
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
    icon=['campus_wifi.ico'],
)
