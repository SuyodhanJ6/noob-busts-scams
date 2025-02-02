import re
from typing import List
from fastapi import HTTPException
from dotenv import load_dotenv
import os
from functools import wraps
from redis import Redis
from src.settings import settings
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, ChatMessage

# Load environment variables from .env file
load_dotenv()

# Access the GROQ_API_KEY
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise EnvironmentError("GROQ_API_KEY is not set in the environment.")

# Initialize Redis client
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

class TextProcessor:
    """Component for text preprocessing"""
    
    def __init__(self):
        self.phone_pattern = r'\+\d{1,3}-\d{6,14}'
        
    def clean_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Normalize phone numbers
        text = self._normalize_phone_numbers(text)
        
        # Remove special characters
        text = re.sub(r'[^\w\s\+\-]', '', text)
        
        return text.strip()
    
    def _normalize_phone_numbers(self, text: str) -> str:
        """Normalize phone numbers to standard format"""
        def replace_number(match):
            number = match.group(0)
            # Ensure format: +XX-XXXXXXXXXX
            return re.sub(r'[\s\-\(\)]', '-', number)
            
        return re.sub(self.phone_pattern, replace_number, text)

def validate_phone_number(phone_number: str) -> str:
    """
    Validate the phone number format.
    
    Args:
        phone_number: The phone number to validate
        
    Returns:
        The validated phone number
        
    Raises:
        HTTPException: If the phone number is invalid
    """
    pattern = r"^\+\d{1,3}-\d{6,14}$"  # Example: +1-1234567890
    
    if not re.match(pattern, phone_number):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid phone number format: {phone_number}. Expected format: +<country_code>-<number>"
        )
    
    return phone_number

def rate_limiter(func):
    """
    Decorator to limit the rate of requests per user.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract user identifier (e.g., IP address or user ID)
        user_id = kwargs.get('user_id', 'default_user')
        
        # Define rate limit parameters
        rate_limit = settings.RATE_LIMIT_CALLS
        time_window = settings.RATE_LIMIT_PERIOD  # in seconds

        # Construct Redis key
        redis_key = f"rate_limit:{user_id}"

        # Get current request count
        request_count = redis_client.get(redis_key)

        if request_count is not None and int(request_count) >= rate_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Only {rate_limit} requests allowed per {time_window // 60} minutes."
            )

        # Increment count and set expiry if it's a new key
        redis_client.incr(redis_key)
        if request_count is None:
            redis_client.expire(redis_key, time_window)

        return await func(*args, **kwargs)

    return wrapper

def convert_message_content_to_string(content: str | list[str | dict]) -> str:
    """Convert message content to a string."""
    if isinstance(content, str):
        return content
    text: list[str] = []
    for content_item in content:
        if isinstance(content_item, str):
            text.append(content_item)
            continue
        if content_item["type"] == "text":
            text.append(content_item["text"])
    return "".join(text)

def infer_chat_message(message: BaseMessage) -> dict:
    """
    Infer the type of chat message and convert it to a dictionary format.
    
    Args:
        message: The message to infer
        
    Returns:
        A dictionary representing the inferred message
    """
    if isinstance(message, HumanMessage):
        return {
            "type": "human",
            "content": convert_message_content_to_string(message.content)
        }
    elif isinstance(message, AIMessage):
        return {
            "type": "ai",
            "content": convert_message_content_to_string(message.content),
            "tool_calls": message.tool_calls if message.tool_calls else None,
            "response_metadata": message.response_metadata if message.response_metadata else None
        }
    elif isinstance(message, ToolMessage):
        return {
            "type": "tool",
            "content": convert_message_content_to_string(message.content),
            "tool_call_id": message.tool_call_id
        }
    elif isinstance(message, ChatMessage):
        if message.role == "custom":
            return {
                "type": "custom",
                "content": "",
                "custom_data": message.content[0]
            }
        raise ValueError(f"Unsupported chat message role: {message.role}")
    else:
        raise ValueError(f"Unsupported message type: {message.__class__.__name__}")

# Additional text processing functions can be added here 