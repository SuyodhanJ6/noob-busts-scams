from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from sqlalchemy.orm import Session

from controller.service import BaseService
from src.monitoring.opik import log_user_activity
from src.entity.config_ent import AppConfig
from src.logger import logger
from src.utils.validators import validate_phone_number
from src.database.db_session import get_db
from src.database.crud import DatabaseManager

router = APIRouter(prefix="/users", tags=["users"])

class UserCreate(BaseModel):
    """User registration request model"""
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, description="User's full name")
    phone: Optional[str] = Field(None, description="User's phone number")

class UserResponse(BaseModel):
    """User registration response model"""
    user_id: int
    email: str
    name: str
    phone: Optional[str] = None
    message: str = "User registered successfully"

class UserService(BaseService):
    def __init__(self, config: AppConfig):
        super().__init__(config)

    @router.post(
        "/register",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Register User",
        description="Register a new user in the system"
    )
    async def register_user(
        self, 
        user: UserCreate,
        db: Session = Depends(get_db)
    ):
        """
        Register a new user with the following information:
        - **email**: Valid email address
        - **name**: User's full name (minimum 2 characters)
        - **phone**: Optional phone number
        """
        try:
            # Initialize database manager
            db_manager = DatabaseManager(db)
            
            # Validate phone if provided
            validated_phone = None
            if user.phone:
                validated_phone = validate_phone_number(user.phone)
            
            # Check if user exists
            existing_user = await db_manager.get_user_by_email(user.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User with this email already exists"
                )
            
            # Create user
            user_data = {
                "email": user.email,
                "name": user.name,
                "phone": validated_phone
            }
            
            new_user = await db_manager.create_user(user_data)
            
            # Log activity
            log_user_activity(
                user_id=new_user.id,
                action="register",
                metadata={"email": user.email}
            )
            
            return UserResponse(
                user_id=new_user.id,
                email=new_user.email,
                name=new_user.name,
                phone=new_user.phone
            )
            
        except HTTPException as he:
            # Re-raise HTTP exceptions
            raise he
        except Exception as e:
            logger.error(f"Error registering user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {str(e)}"
            ) 