import logging
from collections import defaultdict

from fastapi import APIRouter, Depends

from src.schemas.requests import CapacityRequest, CapacitySummaryRequest
from src.core.container import get_repository
from src.repositories.interfaces import AbstractRepository
from src.schemas.responses import (
    CapacityListResponse,
    CapacityResponse,
    DailySummaryListResponse,
    DailySummaryResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["capacity"])


@router.get("/capacity", response_model=CapacityListResponse)
async def get_capacity(
    params: CapacityRequest = Depends(),
    repository: AbstractRepository = Depends(get_repository),
) -> CapacityListResponse:
    capacities = repository.get_capacity(
        origin=params.origin,
        destination=params.destination,
        date=params.date,
    )
    return CapacityListResponse(
        count=len(capacities),
        capacities=[CapacityResponse(**c.model_dump()) for c in capacities],
    )


@router.get("/capacity/summary", response_model=DailySummaryListResponse)
async def get_daily_summary(
    params: CapacitySummaryRequest = Depends(),
    repository: AbstractRepository = Depends(get_repository),
) -> DailySummaryListResponse:
    capacities = repository.get_capacity(
        origin=params.origin,
        destination=params.destination,
        date=params.date,
    )

    daily: dict[str, list] = defaultdict(list)
    for c in capacities:
        daily[c.date].append(c)

    summaries = [
        DailySummaryResponse(
            date=d,
            origin_iata=params.origin,
            destination_iata=params.destination,
            total_flights=len(caps),
            total_volume_m3=round(sum(c.volume_m3 for c in caps), 2),
            total_payload_kg=round(sum(c.payload_kg for c in caps), 2),
        )
        for d, caps in sorted(daily.items())
    ]

    return DailySummaryListResponse(count=len(summaries), summaries=summaries)
