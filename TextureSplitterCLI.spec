# -*- mode: python ; coding: utf-8 -*-
# Builds the command-line tool (split_spritesheet.py) into a single console executable.
# Run via build_windows.bat / build_mac.sh, or directly:
#   pyinstaller --noconfirm TextureSplitterCLI.spec
datas = [("srgb.icc", ".")]

a = Analysis(
    ["split_spritesheet.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    name="TextureSplitterCLI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
)
