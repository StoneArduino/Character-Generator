# -*- mode: python ; coding: utf-8 -*-
import tempfile

block_cipher = None

a = Analysis(
    ['4-Characters.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['wmi', 'win32com.client'],  # 添加需要的模块
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    workpath=tempfile.gettempdir(),
    specpath=tempfile.gettempdir(),
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='字符生成器',  # 设置生成的exe名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 设置为False以隐藏控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='hat_icon-icons.com_74643.ico'  # 如果你有图标文件的话
) 