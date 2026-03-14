import logging

from fastapi import APIRouter, Depends

from src.core.container import get_repository
from src.repositories.interfaces import AbstractRepository
from src.schemas.requests import CapacityRequest, CapacitySummaryRequest
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
    capacity_iter = repository.stream_capacities(origin=params.origin, destination=params.destination, date=params.date)
    capacities = list(capacity_iter)
    return CapacityListResponse(
        count=len(capacities),
        capacities=[CapacityResponse(**c.model_dump()) for c in capacities],
    )


@router.get("/capacity/summary", response_model=DailySummaryListResponse)
async def get_daily_summary(
    params: CapacitySummaryRequest = Depends(),
    repository: AbstractRepository = Depends(get_repository),
) -> DailySummaryListResponse:
    summary_iter = repository.stream_capacity_summary(origin=params.origin, destination=params.destination,
                                                      date=params.date)

    summaries = [
        DailySummaryResponse(**s.model_dump())
        for s in summary_iter
    ]

    return DailySummaryListResponse(count=len(summaries), summaries=summaries)
