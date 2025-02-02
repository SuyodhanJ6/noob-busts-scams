from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.entity.config_ent import AppConfig
from src.logger import logger
from src.utils.rate_limiter import rate_limit
from src.utils.validators import validate_phone_number

router = APIRouter()
security = HTTPBearer()

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

class BaseService:
    def __init__(self, config: AppConfig):
        self.config = config
        
    async def authenticate(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Validate API token"""
        if not credentials or credentials.credentials != self.config.api_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
