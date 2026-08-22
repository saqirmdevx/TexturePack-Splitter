# -*- mode: python ; coding: utf-8 -*-
# Builds the desktop GUI (app.py) into a single windowed executable.
# Run via build_windows.bat / build_mac.sh, or directly:
#   pyinstaller --noconfirm TextureSplitter.spec
import sys

datas = [("srgb.icc", ".")]

a = Analysis(
    ["app.py"],
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
    name="TextureSplitter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="TextureSplitter.app",
        icon="assets/favicon.icns",
        bundle_identifier="com.saqirmdevx.texturesplitter",
        info_plist={"NSHighResolutionCapable": True},
    )
