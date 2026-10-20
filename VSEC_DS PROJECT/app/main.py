"""
Main FastAPI application entry point for RoadCast.
Initializes middleware, registers REST routes, serves static frontend assets,
and provides application health check.
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.api.routes import router as api_router

app = FastAPI(
    title="RoadCast — Historical Traffic Analytics API",
    description="Educational analytics application for exploring historical traffic patterns, volume distributions, weather impacts, and baseline ML models on westbound Interstate 94.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local cross-origin development if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to prevent stale caching during interactive usage
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Mount API router
app.include_router(api_router)

# Mount static frontend directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/health")
def health_check():
    """Application operational status check."""
    return {
        "status": "healthy",
        "service": "RoadCast Historical Traffic Analytics",
        "version": "1.0.0",
        "disclaimer": "Historical traffic analytics service. Not for live navigation."
    }


@app.get("/")
def serve_index():
    """Serves the main single-page application frontend with cache-control headers."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(
            index_path,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )
    return JSONResponse(
        content={
            "message": "RoadCast API is active. Frontend static files loading...",
            "docs": "/docs",
            "health": "/health"
        }
    )
