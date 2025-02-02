from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, ScamReport, ModelMetrics
from src.logger import logger
from src.database.db_session import get_session

class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, session: Session):
        self.db = session
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            raise
    
    async def create_user(self, user_data: dict) -> User:
        """Create new user"""
        try:
            user = User(**user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def search_scams_by_phone(self, phone: str) -> List[ScamReport]:
        """Search scam reports by phone number"""
        try:
            return self.db.query(ScamReport)\
                .filter(ScamReport.scammer_phone == phone)\
                .order_by(ScamReport.created_at.desc())\
                .all()
        except Exception as e:
            logger.error(f"Error searching scams: {str(e)}")
            raise
    
    async def create_scam_report(self, report_data: dict) -> ScamReport:
        """Create new scam report"""
        try:
            report = ScamReport(**report_data)
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating scam report: {str(e)}")
            raise
    
    async def log_model_metric(self, metric_data: dict) -> ModelMetrics:
        """Log model metrics"""
        try:
            metric = ModelMetrics(**metric_data)
            self.db.add(metric)
            self.db.commit()
            self.db.refresh(metric)
            return metric
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging model metric: {str(e)}")
            raise

class ScamCRUD:
    """CRUD operations for scam reports."""
    
    def __init__(self):
        self._session = None
    
    async def _get_session(self) -> AsyncSession:
        """Get database session."""
        if not self._session:
            self._session = await anext(get_session())
        return self._session

    async def create_scam_report(
        self,
        scammer_phone: str,
        description: str,
        reporter_phone: Optional[str] = None,
        reporter_email: Optional[str] = None,
        scam_type: Optional[str] = None
    ) -> ScamReport:
        """
        Create a new scam report.
        
        Args:
            scammer_phone: Phone number of the alleged scammer
            description: Description of the scam
            reporter_phone: Optional reporter's phone number
            reporter_email: Optional reporter's email
            scam_type: Optional type of scam
            
        Returns:
            Created ScamReport instance
        """
        session = await self._get_session()
        
        scam_report = ScamReport(
            scammer_phone=scammer_phone,
            description=description,
            reporter_phone=reporter_phone,
            reporter_email=reporter_email,
            scam_type=scam_type,
            created_at=datetime.utcnow()
        )
        
        try:
            session.add(scam_report)
            await session.commit()
            await session.refresh(scam_report)
            return scam_report
        except Exception as e:
            await session.rollback()
            raise e

    async def get_scam_reports(self, phone_number: str) -> List[ScamReport]:
        """
        Get all scam reports for a phone number.
        
        Args:
            phone_number: Phone number to search for
            
        Returns:
            List of ScamReport instances
        """
        session = await self._get_session()
        
        query = select(ScamReport).where(
            ScamReport.scammer_phone == phone_number
        ).order_by(ScamReport.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()

    async def get_report_by_id(self, report_id: int) -> Optional[ScamReport]:
        """
        Get a specific scam report by ID.
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            ScamReport instance if found, None otherwise
        """
        session = await self._get_session()
        
        query = select(ScamReport).where(ScamReport.id == report_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def update_report(
        self,
        report_id: int,
        **kwargs
    ) -> Optional[ScamReport]:
        """
        Update a scam report.
        
        Args:
            report_id: ID of the report to update
            **kwargs: Fields to update
            
        Returns:
            Updated ScamReport instance if found, None otherwise
        """
        session = await self._get_session()
        
        report = await self.get_report_by_id(report_id)
        if not report:
            return None
            
        for key, value in kwargs.items():
            if hasattr(report, key):
                setattr(report, key, value)
                
        try:
            await session.commit()
            await session.refresh(report)
            return report
        except Exception as e:
            await session.rollback()
            raise e

    async def delete_report(self, report_id: int) -> bool:
        """
        Delete a scam report.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            True if deleted, False if not found
        """
        session = await self._get_session()
        
        report = await self.get_report_by_id(report_id)
        if not report:
            return False
            
        try:
            await session.delete(report)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            raise e

# In your tool
async def some_operation():
    with get_db() as db:
        db_manager = DatabaseManager(db)
        result = await db_manager.search_scams_by_phone(phone_number) 