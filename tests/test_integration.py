import pytest
from sqlalchemy.orm import Session

from src.utils.database import ScamReport, User
from src.utils.db_session import get_db

@pytest.fixture
def db_session():
    with get_db() as session:
        yield session

def test_create_user(db_session: Session):
    user = User(
        email="test@example.com",
        name="Test User",
        phone="+1-1234567890"
    )
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"

def test_create_scam_report(db_session: Session):
    # Create test user
    user = User(
        email="reporter@example.com",
        name="Reporter"
    )
    db_session.add(user)
    db_session.commit()
    
    # Create scam report
    report = ScamReport(
        scammer_phone="+1-9876543210",
        scam_type="FAKE_AUTHORITY",
        description="Test scam description",
        confidence_score=0.95,
        reporter_id=user.id,
        model_version="llama-3-70b"
    )
    db_session.add(report)
    db_session.commit()
    
    assert report.id is not None
    assert report.reporter.email == "reporter@example.com" 