from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all service routers
from controller.service.analysis_service import router as analysis_router
from controller.service.search_service import router as search_router
from controller.service.user_service import router as user_router
from controller.service import router as base_router

from src.logger import logger
from src.monitoring.opik import setup_monitoring
from src.settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up Noob Busts Scams API")
    yield
    # Shutdown
    logger.info("Shutting down Noob Busts Scams API")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Noob Busts Scams",
    description="A tool to combat digital scams with multi-user support",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup monitoring with config
app_config = settings.get_app_config
setup_monitoring(app, app_config.monitoring_config)

# Include all API routes with prefix
app.include_router(base_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

# Add API documentation tags
app.openapi_tags = [
    {
        "name": "analysis",
        "description": "Scam analysis operations"
    },
    {
        "name": "search",
        "description": "Search operations for reported scams"
    },
    {
        "name": "users",
        "description": "User management operations"
    }
]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
