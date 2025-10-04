"""
Shared pytest fixtures for JV Dashboard tests.
Provides test DB, sample models, and mocks.
Easy to change: Add new fixtures here for reuse.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database import Base
from models import (
    ProductTechnology, TargetCompany, Stakeholder, Outreach, Meeting, Deal,
    MarketAlignment, CompanySize, StakeholderRole, OutreachResponse, MeetingStatus, DealStage
)
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test database: In-memory SQLite (no file, auto-cleanup)
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # For in-memory consistency
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables in test DB on session start."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)  # Cleanup after all tests

@pytest.fixture(scope="function")
def db_session():
    """Fresh DB session per test function (rolls back changes)."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def sample_product(db_session):
    """Sample ProductTechnology for tests."""
    product = ProductTechnology(
        name="Test Tech",
        description="Sample product",
        market_alignment=MarketAlignment.HIGH,
        manufacturing_suitability=MarketAlignment.MEDIUM,
        revenue_potential="$1M",
        status="research"
    )
    db_session.add(product)
    db_session.commit()
    return product

@pytest.fixture
def sample_company(db_session, sample_product):
    """Sample TargetCompany linked to product."""
    company = TargetCompany(
        name="Test Corp",
        product_technology_id=sample_product.id,
        industry="Tech",
        size=CompanySize.MEDIUM,
        revenue="$10M",
        contact_info="info@testcorp.com",
        status="identified"
    )
    db_session.add(company)
    db_session.commit()
    return company

@pytest.fixture
def sample_stakeholder(db_session, sample_company):
    """Sample Stakeholder linked to company."""
    stakeholder = Stakeholder(
        company_id=sample_company.id,
        name="John Doe",
        title="CEO",
        email="john@testcorp.com",
        phone="123-456-7890",
        role=StakeholderRole.DECISION_MAKER,
        status="identified",
        linkedin_data='{"profile": "test"}'
    )
    db_session.add(stakeholder)
    db_session.commit()
    return stakeholder

@pytest.fixture
def sample_outreach(db_session, sample_stakeholder):
    """Sample Outreach linked to stakeholder."""
    outreach = Outreach(
        stakeholder_id=sample_stakeholder.id,
        message="Test outreach message",
        notes="Initial contact",
        date=datetime.utcnow() - timedelta(days=1),
        response=OutreachResponse.NO_RESPONSE
    )
    db_session.add(outreach)
    db_session.commit()
    return outreach

@pytest.fixture
def sample_meeting(db_session, sample_outreach):
    """Sample Meeting linked to outreach."""
    meeting = Meeting(
        outreach_id=sample_outreach.id,
        scheduled_date=datetime.utcnow() + timedelta(days=1),
        participants="John Doe, Team Lead",
        agenda="Discuss JV",
        status=MeetingStatus.SCHEDULED
    )
    db_session.add(meeting)
    db_session.commit()
    return meeting

@pytest.fixture
def sample_deal(db_session, sample_meeting):
    """Sample Deal linked to meeting."""
    deal = Deal(
        meeting_id=sample_meeting.id,
        stage=DealStage.INTRO,
        notes="Initial notes",
        assigned_to="user@example.com",
        assigned_at=datetime.utcnow()
    )
    db_session.add(deal)
    db_session.commit()
    return deal

# Mock external services (used in utils and endpoints tests)
@pytest.fixture
def mock_openai():
    """Mock OpenAI client for AI services."""
    with patch('services.openai_service.client') as mock_client:
        mock_response = Mock()
        mock_response.choices[0].message.content = "Mock AI response"
        mock_client.chat.completions.create.return_value = mock_response
        yield mock_client

@pytest.fixture
def mock_gmail():
    """Mock Gmail send_email to return True."""
    with patch('services.gmail_service.send_email') as mock_send:
        mock_send.return_value = True
        yield mock_send

@pytest.fixture
def mock_hunter():
    """Mock Hunter.io verify_email to return valid result."""
    with patch('services.hunter_service.verify_email') as mock_verify:
        mock_verify.return_value = {'result': 'deliverable'}
        yield mock_verify

@pytest.fixture
def test_client():
    """FastAPI TestClient for endpoint tests (with mocked DB)."""
    from fastapi.testclient import TestClient
    from backend import app  # Import your FastAPI app

    # Override get_db for tests (use in-memory session)
    def override_get_db():
        test_db = TestingSessionLocal()
        try:
            yield test_db
        finally:
            test_db.close()

    app.dependency_overrides[database.get_db] = override_get_db  # Note: Import database if needed
    with TestClient(app) as client:
        yield client