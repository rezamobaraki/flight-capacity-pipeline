import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.core import container as container_module  # Renamed for clarity within test if needed
from src.handlers import capacity, health


@pytest.fixture
def app(repository, pipeline):
    # Run pipeline to populate test DB
    pipeline.run()

    app = FastAPI(title="Test")
    app.include_router(health.router)
    app.include_router(capacity.router)

    # Override dependency
    app.dependency_overrides[container_module.get_repository] = lambda: repository
    return app


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestHealthEndpoint:
    @pytest.mark.anyio
    async def test_health_returns_ok(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCapacityEndpoint:
    @pytest.mark.anyio
    async def test_get_all_capacity(self, client):
        response = await client.get("/api/v1/capacity")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["capacities"]) == 2

    @pytest.mark.anyio
    async def test_filter_by_origin(self, client):
        response = await client.get("/api/v1/capacity", params={"origin": "MEM"})
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["capacities"][0]["origin_iata"] == "MEM"

    @pytest.mark.anyio
    async def test_filter_by_route(self, client):
        response = await client.get(
            "/api/v1/capacity",
            params={"origin": "MEM", "destination": "HNL"},
        )
        assert response.status_code == 200
        assert response.json()["count"] == 1

    @pytest.mark.anyio
    async def test_no_results_for_unknown_route(self, client):
        response = await client.get(
            "/api/v1/capacity",
            params={"origin": "ZZZ", "destination": "YYY"},
        )
        assert response.status_code == 200
        assert response.json()["count"] == 0


class TestDailySummaryEndpoint:
    @pytest.mark.anyio
    async def test_daily_summary(self, client):
        response = await client.get(
            "/api/v1/capacity/summary",
            params={"origin": "MEM", "destination": "HNL"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        summary = data["summaries"][0]
        assert summary["total_flights"] == 1
        assert summary["total_volume_m3"] == 74.78

    @pytest.mark.anyio
    async def test_daily_summary_requires_origin_destination(self, client):
        response = await client.get("/api/v1/capacity/summary")
        assert response.status_code == 422

    @pytest.mark.anyio
    async def test_invalid_date_format(self, client):
        response = await client.get(
            "/api/v1/capacity/summary",
            params={"origin": "MEM", "destination": "HNL", "date": "not-a-date"},
        )
        assert response.status_code == 422
