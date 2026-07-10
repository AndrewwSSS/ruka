# -*- mode: python ; coding: utf-8 -*-
# Build with: pyinstaller ruka.spec --noconfirm
# Output: dist/Ruka.exe (single portable file; self-extracts to a temp dir
# on each launch, so startup is a second or two slower than the one-folder
# build, but there's nothing else to keep alongside it).

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/arm_image.jpg', 'resources')],
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
    name='Ruka',
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
)
