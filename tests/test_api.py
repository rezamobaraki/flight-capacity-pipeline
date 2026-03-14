import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def app(container_with_handlers):
	container_with_handlers.pipeline.run()
	from fastapi import FastAPI

	app = FastAPI(title="Test")
	app.include_router(container_with_handlers.health_handler.router)
	app.include_router(container_with_handlers.capacity_handler.router)
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
