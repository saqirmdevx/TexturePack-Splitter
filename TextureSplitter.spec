# -*- mode: python ; coding: utf-8 -*-
# Builds the desktop GUI (gui_app.py) into a single windowed executable.
# Run via build_windows.bat / build_mac.sh, or directly:
#   pyinstaller --noconfirm TextureSplitter.spec
import sys

from version import __version__

datas = [("srgb.icc", "."), ("assets/favicon.png", ".")]

a = Analysis(
    ["gui_app.py"],
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

# Windows EXE version resource (shows up in File Explorer -> Properties -> Details).
# Ignored on other platforms.
version_info = None
if sys.platform == "win32":
    from PyInstaller.utils.win32.versioninfo import (
        FixedFileInfo, StringFileInfo, StringStruct, StringTable, VarFileInfo, VarStruct, VSVersionInfo,
    )
    version_tuple = tuple(int(p) for p in __version__.split(".")) + (0,)
    version_info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=version_tuple, prodvers=version_tuple),
        kids=[
            StringFileInfo([StringTable(
                "040904B0",
                [
                    StringStruct("CompanyName", "saqirmdevx"),
                    StringStruct("FileDescription", "TextureSplitter"),
                    StringStruct("FileVersion", __version__),
                    StringStruct("InternalName", "TextureSplitter"),
                    StringStruct("LegalCopyright", "saqirmdevx"),
                    StringStruct("OriginalFilename", "TextureSplitter.exe"),
                    StringStruct("ProductName", "TextureSplitter"),
                    StringStruct("ProductVersion", __version__),
                ],
            )]),
            VarFileInfo([VarStruct("Translation", [1033, 1200])]),
        ],
    )

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
    icon="assets/favicon.png",
    version=version_info,
)

if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="TextureSplitter.app",
        icon="assets/favicon.png",
        bundle_identifier="com.saqirmdevx.texturesplitter",
        info_plist={
            "NSHighResolutionCapable": True,
            "CFBundleShortVersionString": __version__,
            "CFBundleVersion": __version__,
        },
    )
