
# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

hidden = collect_submodules("app") + ["websockets"]
datas = collect_data_files("app") + [
    ("app/interface/question.tcss", "app/interface"),
    ("app/interface/dashboard.tcss", "app/interface"),
]

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="StemWeek_User_App",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

app = BUNDLE(
    exe,
    name="StemWeek_User_App.app",
    icon=None,
    bundle_identifier=None,
)
