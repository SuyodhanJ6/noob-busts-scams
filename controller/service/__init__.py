from fastapi import APIRouter, HTTPException, status
from src.entity.config_ent import AppConfig
from src.logger import logger
from src.utils.rate_limiter import rate_limit

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

class BaseService:
    """Base service class with common functionality"""
    
    def __init__(self, config: AppConfig):
        self.config = config
            
    @property
    def db(self):
        """Database connection property"""
        from src.database.db_session import get_db
        return next(get_db())
    
    async def validate_request(self, request_data: dict):
        """Common request validation"""
        if not request_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request data is required"
            )
    
    def log_error(self, error: Exception, context: str = ""):
        """Centralized error logging"""
        logger.error(f"Error in {context}: {str(error)}")
