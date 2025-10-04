"""
Unit tests for SQLAlchemy models in models.py.
Tests: Creation, enums, relationships, basic queries.
Run: pytest tests/test_models.py -v
"""
import pytest
from sqlalchemy.exc import IntegrityError
from models import (
    ProductTechnology, TargetCompany, Stakeholder, Outreach, Meeting, Deal,
    MarketAlignment, CompanySize, StakeholderRole, OutreachResponse, MeetingStatus, DealStage
)

class TestModels:
    def test_product_creation(self, db_session, sample_product):
        """Test ProductTechnology creation and fields."""
        assert sample_product.id is not None
        assert sample_product.name == "Test Tech"
        assert sample_product.market_alignment == MarketAlignment.HIGH
        assert sample_product.status == "research"

    def test_company_creation_and_relationship(self, db_session, sample_company, sample_product):
        """Test TargetCompany creation and product relationship."""
        assert sample_company.name == "Test Corp"
        assert sample_company.size == CompanySize.MEDIUM
        assert sample_company.product.id == sample_product.id  # Back-populates works

    def test_stakeholder_creation_and_relationship(self, db_session, sample_stakeholder, sample_company):
        """Test Stakeholder creation, enums, and company relationship."""
        assert sample_stakeholder.name == "John Doe"
        assert sample_stakeholder.role == StakeholderRole.DECISION_MAKER
        assert sample_stakeholder.company.id == sample_company.id
        assert isinstance(sample_stakeholder.linkedin_data, str)  # JSON string

    def test_outreach_creation_and_relationship(self, db_session, sample_outreach, sample_stakeholder):
        """Test Outreach creation, enums, and stakeholder relationship."""
        assert sample_outreach.message == "Test outreach message"
        assert sample_outreach.response == OutreachResponse.NO_RESPONSE
        assert sample_outreach.stakeholder.id == sample_stakeholder.id

    def test_meeting_creation_and_relationship(self, db_session, sample_meeting, sample_outreach):
        """Test Meeting creation, enums, and outreach relationship."""
        assert sample_meeting.agenda == "Discuss JV"
        assert sample_meeting.status == MeetingStatus.SCHEDULED
        assert sample_meeting.outreach.id == sample_outreach.id

    def test_deal_creation_and_relationship(self, db_session, sample_deal, sample_meeting):
        """Test Deal creation, enums, and meeting relationship."""
        assert sample_deal.stage == DealStage.INTRO
        assert sample_deal.assigned_to == "user@example.com"
        assert sample_deal.meeting.id == sample_meeting.id

    def test_enum_validation(self, db_session):
        """Test enum constraints (e.g., invalid value raises error)."""
        invalid_product = ProductTechnology(
            name="Invalid",
            market_alignment="invalid_enum"  # Not in MarketAlignment
        )
        db_session.add(invalid_product)
        with pytest.raises(IntegrityError):
            db_session.commit()  # Should fail on enum check

    def test_relationship_cascade(self, db_session, sample_company):
        """Test deleting parent cascades (if configured; basic check)."""
        # Add stakeholder
        stakeholder = Stakeholder(company_id=sample_company.id, name="Test")
        db_session.add(stakeholder)
        db_session.commit()
        # Query via relationship
        assert len(sample_company.stakeholders) == 1
        # Delete company (in real, add ondelete='CASCADE' in models if needed)
        db_session.delete(sample_company)
        db_session.commit()
        assert db_session.query(Stakeholder).count() == 0  # Assuming no cascade; adjust if added