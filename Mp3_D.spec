# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# 加入 ffmpeg 和 ffprobe
datas = [
    ('ffmpeg.exe', '.'),
    ('ffprobe.exe', '.'),
]

a = Analysis(
    ['Mp3_D.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['requests'], # 確保 requests 被打包
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
    name='Mp3_D',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False, # 設為 False 隱藏黑窗
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)