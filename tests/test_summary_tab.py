import pytest
from httpx import AsyncClient, ASGITransport
from server import app

@pytest.mark.asyncio
async def test_get_project_summary_success():
    """Verify GET /api/projects/{id}/summary returns complete feature-level metrics & benchmarks."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/projects/AI-001/summary")
        assert response.status_code == 200
        data = response.json()
        
        # 1. Core top-level contract keys
        assert "project" in data
        assert "overview" in data
        assert "benchmarks" in data
        assert "features" in data

        # 2. Project metadata
        assert data["project"]["id"] == "AI-001"
        assert data["project"]["project"] == "MedVoice V2"
        assert "domain" in data["project"]
        assert "phase" in data["project"]

        # 3. Aggregation & financial metrics
        overview = data["overview"]
        assert overview["total_features"] > 0
        assert overview["implemented_features"] >= 0
        assert "implementation_pct" in overview
        assert "financial_metrics" in overview
        fm = overview["financial_metrics"]
        assert "revenue_impact_sar" in fm
        assert "net_profit_sar" in fm
        assert "time_saved_hrs" in fm
        assert "csat_score" in fm

        # 4. Benchmarks structure & status mapping
        assert isinstance(data["benchmarks"], list)
        assert len(data["benchmarks"]) > 0
        for b in data["benchmarks"]:
            assert "metric_key" in b
            assert "metric_name" in b
            assert "actual_value" in b
            assert "status" in b
            assert b["status"] in ["EXCEEDING", "ON_TARGET", "BELOW_BENCHMARK"]

        # 5. Granular feature-level deliverables & impact attribution
        assert isinstance(data["features"], list)
        assert len(data["features"]) > 0
        for f in data["features"]:
            assert "req_id" in f
            assert "feature_name" in f
            assert "category" in f
            assert "description" in f
            assert "status" in f
            assert "business_impact" in f
            assert "financial_impact_sar" in f
            assert "time_saved_hrs" in f

@pytest.mark.asyncio
async def test_get_project_summary_not_found():
    """Verify 404 is returned when an invalid project ID is requested."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/projects/NON-EXISTENT-999/summary")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_frontend_default_tab_is_summary():
    """Verify index.html serves Vite app with Executive Summary configured as default tab."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        html = response.text
        # Check SPA title and bundle linkage
        assert "Andalusia Healthcare Portfolio Dashboard" in html
        assert 'id="root"' in html
