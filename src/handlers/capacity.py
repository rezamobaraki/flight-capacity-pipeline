import logging
from collections import defaultdict
from typing import Optional

from fastapi import APIRouter, Query

from src.repositories.interfaces import AbstractRepository
from src.schemas.responses import (
    CapacityListResponse,
    CapacityResponse,
    DailySummaryListResponse,
    DailySummaryResponse,
)

logger = logging.getLogger(__name__)


class CapacityHandler:
    def __init__(self, repository: AbstractRepository):
        self._repository = repository
        self.router = APIRouter(prefix="/api/v1", tags=["capacity"])
        self._register_routes()

    def _register_routes(self) -> None:
        self.router.add_api_route(
            "/capacity",
            self.get_capacity,
            methods=["GET"],
            response_model=CapacityListResponse,
        )
        self.router.add_api_route(
            "/capacity/summary",
            self.get_daily_summary,
            methods=["GET"],
            response_model=DailySummaryListResponse,
        )

    async def get_capacity(
        self,
        origin: Optional[str] = Query(None, min_length=3, max_length=4),
        destination: Optional[str] = Query(None, min_length=3, max_length=4),
        date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    ) -> CapacityListResponse:
        capacities = self._repository.get_capacity(
            origin=origin,
            destination=destination,
            date=date,
        )
        return CapacityListResponse(
            count=len(capacities),
            capacities=[CapacityResponse(**c.model_dump()) for c in capacities],
        )

    async def get_daily_summary(
        self,
        origin: str = Query(..., min_length=3, max_length=4),
        destination: str = Query(..., min_length=3, max_length=4),
        date: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    ) -> DailySummaryListResponse:
        capacities = self._repository.get_capacity(
            origin=origin,
            destination=destination,
            date=date,
        )

        daily: dict[str, list] = defaultdict(list)
        for c in capacities:
            daily[c.date].append(c)

        summaries = [
            DailySummaryResponse(
                date=d,
                origin_iata=origin.upper(),
                destination_iata=destination.upper(),
                total_flights=len(caps),
                total_volume_m3=round(sum(c.volume_m3 for c in caps), 2),
                total_payload_kg=round(sum(c.payload_kg for c in caps), 2),
            )
            for d, caps in sorted(daily.items())
        ]

        return DailySummaryListResponse(count=len(summaries), summaries=summaries)
