import pytest
from httpx import AsyncClient, ASGITransport
from server import app

@pytest.mark.asyncio
async def test_get_project_summary_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/projects/AI-001/summary")
        assert response.status_code == 200
        data = response.json()
        
        # Core keys
        assert "project" in data
        assert "overview" in data
        assert "benchmarks" in data
        assert "features" in data

        # Project level verification
        assert data["project"]["id"] == "AI-001"
        assert data["project"]["project"] == "MedVoice V2"

        # Overview verification
        overview = data["overview"]
        assert overview["total_features"] > 0
        assert overview["implemented_features"] >= 0
        assert "implementation_pct" in overview
        assert "financial_metrics" in overview

        # Benchmarks structure
        assert isinstance(data["benchmarks"], list)
        assert len(data["benchmarks"]) > 0
        b0 = data["benchmarks"][0]
        assert "metric_key" in b0
        assert "actual_value" in b0
        assert "status" in b0
        assert b0["status"] in ["EXCEEDING", "ON_TARGET", "BELOW_BENCHMARK"]

        # Features structure & attribution
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
        f0 = data["features"][0]
        assert "req_id" in f0
        assert "feature_name" in f0
        assert "business_impact" in f0
        assert "financial_impact_sar" in f0
        assert "time_saved_hrs" in f0

@pytest.mark.asyncio
async def test_get_project_summary_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/projects/NON-EXISTENT-999/summary")
        assert response.status_code == 404
