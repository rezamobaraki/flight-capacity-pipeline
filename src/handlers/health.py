from fastapi import APIRouter

from src.schemas.responses import HealthResponse


class HealthHandler:
    def __init__(self):
        self.router = APIRouter(tags=["health"])
        self.router.add_api_route("/health", self.health_check, methods=["GET"])

    async def health_check(self) -> HealthResponse:
        return HealthResponse(status="healthy")
