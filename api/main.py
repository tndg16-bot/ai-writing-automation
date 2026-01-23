"""FastAPI main application"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import generate, history, stats, health, analyze


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager"""
    # Startup
    print("Starting AI Writing API...")
    yield
    # Shutdown
    print("Shutting down AI Writing API...")


app = FastAPI(
    title="AI Writing Automation API",
    description="FastAPI backend for AI Writing Automation - Phase 10",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate.router)
app.include_router(history.router)
app.include_router(stats.router)
app.include_router(health.router)
app.include_router(analyze.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "AI Writing Automation API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
