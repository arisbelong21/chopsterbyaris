"""Complete Cheat Clip PRO frontend embedded as an isolated Chopster workspace."""
from __future__ import annotations

import threading
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QUrl, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QStackedLayout, QVBoxLayout, QWidget,
)

from chopster.app.paths import user_data_dir
from chopster.auto_clip_studio.web_runtime import runtime
from chopster.ui.theme import THEMES

try:
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile, QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except Exception:
    WEBENGINE_AVAILABLE = False


class AutoClipStudioPage(QWidget):
    runtime_ready = Signal(str)
    runtime_failed = Signal(str)

    def __init__(self, app, theme="dark", parent=None):
        super().__init__(parent)
        self.app=app; self._theme=theme; self._running=False; self._profile=None; self.web=None
        C=THEMES.get(theme,THEMES["dark"])
        self.setObjectName("autoClipStudioWeb")
        self.setStyleSheet(f"QWidget#autoClipStudioWeb{{background:#080b16;}} QFrame#webLoader{{background:{C['PANEL']};border:1px solid {C['BORDER']};border-radius:18px;}}")
        root=QStackedLayout(self); root.setContentsMargins(0,0,0,0); self._stack=root
        loader=QWidget(); ll=QVBoxLayout(loader); ll.setContentsMargins(40,40,40,40); ll.addStretch()
        card=QFrame(); card.setObjectName("webLoader"); card.setMaximumWidth(580); cl=QVBoxLayout(card); cl.setContentsMargins(32,30,32,30); cl.setSpacing(12)
        icon=QLabel("⚡"); icon.setAlignment(Qt.AlignCenter); icon.setStyleSheet(f"font-size:38px;color:{C['GOLD']};"); cl.addWidget(icon)
        self.loader_title=QLabel("Starting Auto Clip Studio"); self.loader_title.setAlignment(Qt.AlignCenter); self.loader_title.setStyleSheet(f"font-size:22px;font-weight:800;color:{C['TEXT']};"); cl.addWidget(self.loader_title)
        self.loader_text=QLabel("Loading the complete Cheat Clip workspace and media engine…"); self.loader_text.setAlignment(Qt.AlignCenter); self.loader_text.setWordWrap(True); self.loader_text.setStyleSheet(f"color:{C['MUTED']};"); cl.addWidget(self.loader_text)
        self.retry=QPushButton("Retry"); self.retry.setObjectName("primary"); self.retry.hide(); self.retry.clicked.connect(self._start); cl.addWidget(self.retry)
        line=QHBoxLayout(); line.addStretch(); line.addWidget(card); line.addStretch(); ll.addLayout(line); ll.addStretch(); root.addWidget(loader); self._loader=loader
        self.runtime_ready.connect(self._open_runtime); self.runtime_failed.connect(self._show_error)
        QTimer.singleShot(0,self._start)

    def _start(self):
        self.retry.hide(); self.loader_title.setText("Starting Auto Clip Studio"); self.loader_text.setText("Loading the complete Cheat Clip workspace and media engine…")
        if not WEBENGINE_AVAILABLE:
            self._show_error("Qt WebEngine is not installed. Reinstall dependencies from requirements.txt.")
            return
        def worker():
            try: self.runtime_ready.emit(runtime.start().url)
            except Exception as exc: self.runtime_failed.emit(str(exc))
        threading.Thread(target=worker,daemon=True,name="acs-runtime-loader").start()

    def _open_runtime(self,url):
        if self.web is None:
            data=user_data_dir()/"AutoClipStudio"/"web_profile"; cache=user_data_dir()/"AutoClipStudio"/"web_cache"
            data.mkdir(parents=True,exist_ok=True); cache.mkdir(parents=True,exist_ok=True)
            self._profile=QWebEngineProfile("ChopsterAutoClipStudio",self)
            self._profile.setPersistentStoragePath(str(data)); self._profile.setCachePath(str(cache))
            self._profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
            self._profile.downloadRequested.connect(self._accept_download)
            self.web=QWebEngineView(self); self.web.setPage(QWebEnginePage(self._profile,self.web))
            settings=self.web.settings(); settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture,False); settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled,True); settings.setAttribute(QWebEngineSettings.LocalStorageEnabled,True)
            self.web.loadStarted.connect(lambda:setattr(self,"_running",True)); self.web.loadFinished.connect(lambda _ok:setattr(self,"_running",False))
            self._stack.addWidget(self.web)
        self.web.setUrl(QUrl(url)); self._stack.setCurrentWidget(self.web)

    def _accept_download(self,item):
        from chopster.auto_clip_studio.engine.video_engine import EXPORTS_DIR
        Path(EXPORTS_DIR).mkdir(parents=True,exist_ok=True)
        item.setDownloadDirectory(str(EXPORTS_DIR)); item.accept()

    def _show_error(self,message):
        self._running=False; self._stack.setCurrentWidget(self._loader); self.loader_title.setText("Auto Clip Studio could not start"); self.loader_text.setText(message); self.retry.show()

    def set_compact(self,compact):
        pass

    def has_active_jobs(self):
        """Report backend work so Chopster does not exit mid-render/download."""
        try:
            from chopster.auto_clip_studio.engine.services.download_service import (
                raw_clip_download_jobs, raw_download_jobs,
            )
            from chopster.auto_clip_studio.engine.services.render_service import RENDER_BATCHES
            render_busy=any(v.get("overall_status")=="running" for v in RENDER_BATCHES.values())
            raw_busy=any(v.get("status") in {"pending","downloading"} for v in raw_download_jobs.values())
            clip_busy=any(v.get("status") in {"pending","downloading"} for v in raw_clip_download_jobs.values())
            return render_busy or raw_busy or clip_busy
        except Exception:
            return bool(self._running)

    def shutdown(self):
        runtime.stop()
