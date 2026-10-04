# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

hiddenimports = ['yt_dlp', 'PIL', 'av', 'ctranslate2', 'faster_whisper', 'cv2', 'chopster.ai.orchestrator', 'chopster.ai.local_provider', 'chopster.ai.embedded_gemini', 'fastapi', 'google.genai', 'youtube_transcript_api', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets']
hiddenimports += collect_submodules('yt_dlp')
hiddenimports += collect_submodules('chopster.auto_clip_studio.engine')

datas = [('resources', 'resources'), ('browser_extension', 'browser_extension'),
         ('chopster/auto_clip_studio/engine/fonts', 'chopster/auto_clip_studio/engine/fonts'),
         ('chopster/auto_clip_studio/engine/cascades', 'chopster/auto_clip_studio/engine/cascades'),
         ('chopster/auto_clip_studio/engine/haarcascade_frontalface_default.xml', 'chopster/auto_clip_studio/engine'),
         ('chopster/auto_clip_studio/web_dist', 'chopster/auto_clip_studio/web_dist'),
         ('chopster/auto_clip_studio/web_source', 'chopster/auto_clip_studio/web_source')]
try:
    datas += collect_data_files('cv2')
except Exception:
    pass
binaries = []
for pkg in ('faster_whisper', 'ctranslate2', 'av'):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=list(dict.fromkeys(hiddenimports)),
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
    [],
    exclude_binaries=True,
    name='Chopster by Aris',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icons/app.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Chopster by Aris',
)
