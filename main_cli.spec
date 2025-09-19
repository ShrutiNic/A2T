# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_cli.py'],
    pathex=[],
    binaries=[],
    datas=[('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\Accolade Logo Without Background 3.png', '.'), ('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\AccoladeLogoWithoutBackground.png', '.'), ('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\background.gif', '.'), ('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\Button_Setup.png', '.'), ('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\config.toml', '.'), ('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\src\\PCAN-UDS.dll', '.'), ('E:\\Project\\A2T\\aepl_python_uds_stack_v0.3_Commn - Rel_02 1\\aepl_python_uds_stack_v0.3_Commn - Rel_02\\A2T config & Certificate flashing\\AccoladeBackground.png', '.')],
    hiddenimports=[],
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
    name='main_cli',
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
)
