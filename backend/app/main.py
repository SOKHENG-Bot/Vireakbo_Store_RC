import logging
import time
from contextlib import asynccontextmanager
from typing import Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.userRoute import userRoutes
from app.core.database import databaseManager
from app.core.settings import getSettings
from app.models import orderModel, userModel  # noqa: F401

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup and shutdown"""
    startupStart = time.time()
    try:
        await _initializeServices(app, startupStart)
    except Exception as e:
        await _handleStartupError(startupStart, e)
        raise
    yield


async def _initializeServices(app: FastAPI, startupStart: float):
    """initialize all application services during startup"""

    databaseDuration = await _initDatabase()

    totalStartupDuration = int((time.time() - startupStart) * 1000)
    logger.info(
        "Service started successfully",
        extra={
            "total_startup_duration_ms": totalStartupDuration,
            "database_init_ms": databaseDuration,
        },
    )


async def _initDatabase() -> int:
    """Initialize database"""
    startTime = time.time()
    await databaseManager.createTables()
    duration = int((time.time() - startTime) * 1000)
    logger.info(
        "Database tables created",
        extra={"duration_ms": duration},
    )
    return duration


async def _handleStartupError(startupStart: float, error: Exception) -> None:
    """Handle startup error with logging"""
    logger.error(
        "Failed to startup service",
        exc_info=True,
        extra={
            "startup_duration_ms": int((time.time() - startupStart) * 1000),
            "error_type": type(error).__name__,
        },
    )


# Application Factory
def createApp() -> FastAPI:
    """Create and configue the FastAPI application."""
    app = FastAPI(
        title=getSettings.APP_NAME,
        version=getSettings.APP_VERSION,
        debug=getSettings.DEBUG,
        lifespan=lifespan,
        openapi_url="/openapi.json" if getSettings.DEBUG else None,
        docs_url="/docs" if getSettings.DEBUG else None,
        redoc_url="/redoc" if getSettings.DEBUG else None,
    )

    # Setup application components
    _setupCors(app)
    _setupRoutes(app)

    return app


def _setupCors(app: FastAPI) -> None:
    """Configure CORS settings"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=getSettings.CORS_ORIGINS,
        allow_credentials=getSettings.CORS_CREDENTIALS,
        allow_methods=getSettings.CORS_METHODS,
        allow_headers=getSettings.CORS_HEADERS,
    )

    logger.info(
        "CORS Middleware configured",
        extra={
            "allowed_origins": len(getSettings.CORS_ORIGINS),
            "credentials_allowed": getSettings.CORS_CREDENTIALS,
        },
    )


def _setupRoutes(app: FastAPI) -> None:
    """Register application routes."""
    routerInfo: List[dict[str, Any]] = []

    # User routes
    app.include_router(userRoutes, prefix="/api/v1/users", tags=["Users"])
    routerInfo.append(
        {
            "route": "user",
            "prefix": "/api/v1/users",
            "tags": ["Users"],
        }
    )

    logger.info(
        "Registering application routes",
        extra={
            "route_count": len(routerInfo),
            "routers": routerInfo,
        },
    )
    return


app = createApp()
