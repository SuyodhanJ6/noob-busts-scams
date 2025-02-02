import re
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr

def validate_phone_number(phone: str) -> str:
    """
    Validate phone number format.
    Expected format: +XX-XXXXXXXXXX (e.g., +91-1234567890)
    """
    pattern = r'^\+\d{1,3}-\d{6,14}$'
    if not re.match(pattern, phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid phone number format. Use format: +XX-XXXXXXXXXX"
        )
    return phone

def validate_email(email: EmailStr) -> bool:
    """
    Additional email validation if needed beyond Pydantic's EmailStr
    """
    # Add custom email validation rules here if needed
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required"
        )
    return True

def validate_description(description: str) -> str:
    """
    Validate scam description
    """
    if not description or len(description.strip()) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description must be at least 10 characters long"
        )
    return description.strip()

def validate_scam_type(scam_type: str, valid_types: list[str]) -> str:
    """
    Validate scam type against list of valid types
    """
    if scam_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scam type. Must be one of: {', '.join(valid_types)}"
        )
    return scam_type

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters
    """
    # Remove HTML tags and special characters
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'[<>{}[\]()\'"]', '', text)
    return text.strip()

def validate_confidence_score(score: float) -> float:
    """
    Validate confidence score is between 0 and 1
    """
    if not 0 <= score <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confidence score must be between 0 and 1"
        )
    return score

def validate_model_version(version: str) -> str:
    """
    Validate model version format
    """
    pattern = r'^[a-zA-Z0-9\-\.]+$'
    if not re.match(pattern, version):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid model version format"
        )
    return version 