"""
Integration tests for FastAPI endpoints in routers/.
Uses TestClient to simulate HTTP requests.
Mocks DB/services.
Run: pytest tests/test_endpoints.py -v
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import status
from routers import deals, outreaches, meetings, analytics  # Import routers
from backend import app  # Your main app
from models import DealStage, OutreachResponse, MeetingStatus

class TestEndpoints:
    def setup_method(self):
        """Setup: Include routers in test app if not already."""
        # Ensure routers are included (for test isolation)
        if not any(r.prefix == "/api/v1/deals" for r in app.routes):
            app.include_router(deals.router, prefix="/api/v1")
            app.include_router(outreaches.router, prefix="/api/v1")
            app.include_router(meetings.router, prefix="/api/v1")
            app.include_router(analytics.router, prefix="/api/v1")

    @pytest.fixture(autouse=True)
    def client(self, test_client):
        """Use TestClient from conftest.py."""
        return test_client

    def test_root_endpoint(self, client):
        """Test root health check."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["message"] == "JV Partner Identification API is running!"

    def test_create_deal_success(self, client, sample_meeting):
        """Test POST /api/v1/deals/ - Success."""
        payload = {
            "meeting_id": sample_meeting.id,
            "stage": "intro",
            "notes": "Test deal",
            "assigned_to": "test@user.com"
        }
        response = client.post("/api/v1/deals/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["message"] == "Deal created"

    def test_create_deal_invalid_meeting(self, client):
        """Test POST /api/v1/deals/ - 404 for invalid meeting_id."""
        payload = {"meeting_id": 999, "stage": "intro"}  # Non-existent
        response = client.post("/api/v1/deals/", json=payload)
        assert response.status_code == 404
        assert "Meeting not found" in response.json()["detail"]

    def test_list_deals(self, client, sample_deal):
        """Test GET /api/v1/deals/ - List deals."""
        response = client.get("/api/v1/deals/")
        assert response.status_code == 200
        deals = response.json()
        assert len(deals) >= 1
        assert deals[0]["id"] == sample_deal.id
        assert deals[0]["stage"] == "intro"

    def test_update_deal_stage(self, client, sample_deal):
        """Test PUT /api/v1/deals/{id}/stage - Update stage."""
        response = client.put(f"/api/v1/deals/{sample_deal.id}/stage", json={"stage": "negotiation"})
        assert response.status_code == 200
        assert response.json()["message"] == "Deal stage updated"

    def test_create_outreach_success(self, client, sample_stakeholder):
        """Test POST /api/v1/outreaches/ - Success."""
        payload = {
            "stakeholder