import re
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from fastapi import HTTPException, status
from pydantic import EmailStr

from src.constants import JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.settings import settings

def create_access_token(data: Dict[str, Any]) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)

def validate_phone_number(phone: str) -> str:
    """Validate and format phone number"""
    pattern = r'^\+\d{1,3}-\d{6,14}$'
    if not re.match(pattern, phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Use format: +XX-XXXXXXXXXX"
        )
    return phone

def validate_email(email: EmailStr) -> bool:
    """Additional email validation if needed"""
    # Add custom email validation rules here
    return True

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    # Remove potentially dangerous characters
    text = re.sub(r'[<>{}[\]()\'"]', '', text)
    return text.strip()
