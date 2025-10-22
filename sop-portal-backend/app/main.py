from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config.settings import settings
from app.config.database import db
from app.config.indexes import create_performance_indexes
from app.services.settings_service import SettingsService
from app.utils.scheduler import BackgroundScheduler
from app.middleware.rate_limiter import RateLimiterMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: BackgroundScheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global scheduler

    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Connect to database
    await db.connect_db()
    database = db.get_database()

    # Create performance indexes
    logger.info("Creating database indexes...")
    await create_performance_indexes(database)

    # Initialize default settings
    logger.info("Initializing default settings...")
    settings_service = SettingsService(database)
    await settings_service.initialize_default_settings()

    # Start background scheduler
    logger.info("Starting background scheduler...")
    scheduler = BackgroundScheduler(database)
    scheduler.start()

    yield

    # Shutdown
    logger.info("Shutting down application")

    # Stop scheduler
    if scheduler:
        scheduler.shutdown()

    await db.close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sales & Operations Planning Portal API",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimiterMiddleware, requests_per_minute=60)


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


# Redirect docs endpoints to the correct location
@app.get("/docs")
async def redirect_docs():
    """Redirect /docs to /api/docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")


@app.get("/api/v1/docs")
async def redirect_v1_docs():
    """Redirect /api/v1/docs to /api/docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        database = db.get_database()
        await database.command('ping')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status,
        "version": settings.APP_VERSION
    }


# API v1 router
from app.routers import api_router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
