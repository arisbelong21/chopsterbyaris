import logging
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Initialize environment and configuration
import chopster.auto_clip_studio.engine.config
from chopster.auto_clip_studio.engine.config import logger
from chopster.auto_clip_studio.engine.routers import (
    analyze_router,
    cookies_router,
    downloads_router,
    media_router,
    render_router,
    system_router,
)
# Re-exports for backwards compatibility
from chopster.auto_clip_studio.engine.schemas.analyze import (
    AnalyzeRequest,
    AnalyzeResponse,
    HeatmapPoint,
    TranscriptLine,
    VideoAnalysis,
    ViralClip,
    ViralClipGemini,
)
from chopster.auto_clip_studio.engine.schemas.downloads import (
    CookiesSaveRequest,
    RawClipDownloadRequest,
    RawVideoDownloadRequest,
)
from chopster.auto_clip_studio.engine.schemas.render import (
    RenderBatchRequest,
    RenderSettingsModel,
    RetryBatchRequest,
)
from chopster.auto_clip_studio.engine.services.download_service import (
    raw_clip_download_jobs,
    raw_download_jobs,
)
from chopster.auto_clip_studio.engine.services.render_service import (
    BATCH_REQUESTS,
    RENDER_BATCHES,
)

# Initialize FastAPI Application
app = FastAPI(
    title="CHEAT CLIP PRO API",
    description="High-performance backend API for Cheat Clip Pro auto-clipper and video studio",
    version="2.0.0"
)

# CORS configuration supporting configurable ALLOWED_ORIGINS and local development
allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "").strip()
if allowed_origins_env:
    allow_origins = [orig.strip() for orig in allowed_origins_env.split(",") if orig.strip()]
else:
    allow_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=r"^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Adds standard security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Include Modular Routers
app.include_router(analyze_router)
app.include_router(render_router)
app.include_router(media_router)
app.include_router(cookies_router)
app.include_router(downloads_router)
app.include_router(system_router)

logger.info("Cheat Clip PRO backend routers mounted successfully.")

# Serve the complete original React frontend inside Chopster.  This mount is
# registered after every /api route so API resolution keeps priority.
WEB_DIST = Path(__file__).resolve().parent.parent / "web_dist"
if WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIST), html=True), name="auto-clip-studio-ui")

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "chopster.auto_clip_studio.engine.main:app",
        host=host, port=port, reload=True
    )
