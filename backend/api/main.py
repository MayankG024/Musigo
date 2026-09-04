"""Main FastAPI application for Musigo"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import uvicorn

from api.routers import auth, music, discovery, playlists, users, songs, favorites, activity, health
from api.routers import user_compat
from api.routers import recommendations
from api.core.config import settings, print_config_validation
from api.core.database import init_db
from api.core import errors as error_handlers
from api.core.rate_limit import setup_rate_limiting
from rag_system.vector_store import init_vector_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup and cleanup on shutdown"""
    # Startup
    print("🚀 Starting Musigo API...")
    print_config_validation()  # Validate configuration
    await init_db()
    require_chroma = os.getenv("REQUIRE_CHROMA", "true").lower() in {"1", "true", "yes"}
    try:
        await init_vector_store()
    except Exception as e:
        if require_chroma:
            raise
        else:
            print(f"⚠️ Vector store initialization skipped: {e}")
    yield
    # Shutdown
    print("👋 Shutting down API...")


app = FastAPI(
    title="Musigo",
    description="Discover music through AI-powered recommendations and RAG",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup rate limiting
setup_rate_limiting(app)

# Register error handlers (after app creation, before router inclusion)
app.add_exception_handler(HTTPException, error_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, error_handlers.validation_exception_handler)
app.add_exception_handler(Exception, error_handlers.generic_exception_handler)

# Include routers
# Health checks (no auth required, at root level for load balancers)
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(music.router, prefix="/api/music", tags=["music"])
app.include_router(songs.router, prefix="/api/songs", tags=["songs"])
app.include_router(discovery.router, prefix="/api/discovery", tags=["discovery"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])  # exposes /api/recommendations/recommend
app.include_router(playlists.router, prefix="/api/playlists", tags=["playlists"])
app.include_router(favorites.router, prefix="/api/user", tags=["favorites"])  # /api/user/favorites
app.include_router(activity.router, prefix="/api/user", tags=["activity"])  # /api/user/activity
app.include_router(user_compat.router, prefix="/api/user", tags=["user"])  # /api/user/history etc


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Musigo API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


def main():
    """Run the application"""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
