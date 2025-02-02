from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional

from controller.service import BaseService
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
            
            # Log activity
            log_user_activity(user_id=new_user.id, action="register")
            
            return {
                "user_id": new_user.id,
                "email": new_user.email,
                "name": new_user.name
            }
            
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 