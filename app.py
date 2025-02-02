from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from controller.service import router as api_router
from src.logger import logger
from src.monitoring.opik import setup_monitoring
from src.utils.config import Settings

# Load settings
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="Noob Busts Scams",
    description="A tool to combat digital scams with multi-user support",
    version="1.0.0",
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup monitoring
setup_monitoring(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Noob Busts Scams API")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Noob Busts Scams API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
