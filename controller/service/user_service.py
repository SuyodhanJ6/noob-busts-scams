from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from src.utils.auth import create_access_token
from src.monitoring.opik import log_user_activity
from src.entity.config_ent import AppConfig
from src.logger import logger

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None

class UserService(BaseService):
    def __init__(self, config: AppConfig):
        super().__init__(config)

    @router.post("/register")
    async def register_user(self, user: UserCreate):
        """Register a new user"""
        try:
            # Check if user exists
            existing_user = await self.db.get_user_by_email(user.email)
            if existing_user:
                raise HTTPException(status_code=400, detail="User already exists")
            
            # Create user
            new_user = await self.db.create_user(user)
            
            # Generate token
            token = create_access_token({"sub": new_user.id})
            
            # Log activity
            log_user_activity(user_id=new_user.id, action="register")
            
            return {
                "access_token": token,
                "token_type": "bearer"
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 