"""
Unit tests for utils.py functions.
Tests: Exports (CSV/PDF), follow-ups, date formatting.
Mocks external services.
Run: pytest tests/test_utils.py -v
"""
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import pandas as pd
from utils import (
    check_and_send_followups, export_to_csv, export_to_pdf, format_date,
    push_to_hubspot
)
from models import Outreach, OutreachResponse
from datetime import datetime, timedelta

class TestUtils:
    def test_format_date(self):
        """Test date formatting helper."""
        iso_date = "2023-10-01T12:00:00"
        formatted = format_date(iso_date)
        assert formatted == "2023-10-01 12:00"

    def test_export_to_csv(self, sample_deal):
        """Test CSV export from list of dicts."""
        data = [{"id": sample_deal.id, "stage": "intro", "notes": "test"}]
        csv_content = export_to_csv(data, "test_export")
        df = pd.read_csv(StringIO(csv_content))
        assert len(df) == 1
        assert df.iloc[0]['id'] == sample_deal.id

    @patch('utils.export_to_pdf')  # Mock ReportLab (avoids file I/O in tests)
    def test_export_to_pdf(self, mock_pdf):
        """Test PDF export (mocks canvas to check call)."""
        data = [{"id": 1, "notes": "test"}]
        result = export_to_pdf(data, "test_report", "Test Title")
        mock_pdf.assert_called_once()  # Verifies function called
        assert "test_report.pdf" in result

    def test_check_and_send_followups_no_action(self, db_session, mock_openai, mock_gmail):
        """Test follow-ups: No old outreaches → 0 sent."""
        # Create recent outreach (not old)
        recent_outreach = Outreach(
            message="Recent", response=OutreachResponse.NO_RESPONSE,
            date=datetime.utcnow()  # Not >5 days old
        )
        db_session.add(recent_outreach)
        db_session.commit()
        sent_count = check_and_send_followups(db_session)
        assert sent_count == 0

    def test_check_and_send_followups_sends_email(self, db_session, sample_outreach, mock_openai, mock_gmail):
        """Test follow-ups: Old outreach → AI email sent, status updated."""
        # Make outreach old (>5 days)
        sample_outreach.date = datetime.utcnow() - timedelta(days=6)
        sample_outreach.response = OutreachResponse.NO_RESPONSE
        db_session.commit()
        
        # Mock stakeholder/company for email
        sample_outreach.stakeholder.name = "Test User"
        sample_outreach.stakeholder.company.name = "Test Co"
        sample_outreach.stakeholder.email = "test@email.com"
        db_session.commit()
        
        sent_count = check_and_send_followups(db_session)
        assert sent_count == 1
        # Check status updated
        db_session.refresh(sample_outreach)
        assert sample_outreach.response == OutreachResponse.FOLLOW_UP_NEEDED
        assert sample_outreach.follow_up_date is not None
        mock_gmail.assert_called_once()  # Email sent

    @patch('utils.push_to_hubspot')  # Mock HubSpot service
    def test_push_to_hubspot(self, mock_hubspot):
        """Test HubSpot push (mocks service call)."""
        contact_data = {'email': 'test@example.com', 'firstname': 'John'}
        push_to_hubspot(contact_data)
        mock_hubspot.assert_called_once_with(contact_data)  # From services.hubspot_service