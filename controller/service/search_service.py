from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.utils.validators import validate_phone_number
from src.monitoring.opik import log_search

router = APIRouter(prefix="/search", tags=["search"])

class SearchQuery(BaseModel):
    phone_number: str

class SearchService(BaseService):
    def __init__(self, config: AppConfig):
        super().__init__(config)

    @router.get("/phone/{phone_number}")
    async def search_phone(self, phone_number: str):
        """Search for reported scams by phone number"""
        try:
            # Validate phone number
            validated_number = validate_phone_number(phone_number)
            
            # Search in database
            results = await self.db.search_scams_by_phone(validated_number)
            
            # Log search
            log_search(phone_number=validated_number, results_count=len(results))
            
            return {
                "phone_number": validated_number,
                "reports_count": len(results),
                "reports": results
            }
            
        except Exception as e:
            logger.error(f"Error searching phone number: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e)) 