"""Эндпоинт поиска свободных слотов."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.services.scheduler import Attendee, FreeSlot, find_slots

router = APIRouter()


class SlotsRequest(BaseModel):
    day: str = Field(min_length=10, max_length=10)
    duration_min: int = Field(ge=1, le=480)
    work_start: str = Field(default="", max_length=5)
    work_end: str = Field(default="", max_length=5)
    attendees: list[Attendee] = Field(min_length=1, max_length=50)


class SlotsResponse(BaseModel):
    day: str
    slots: list[FreeSlot]


@router.post("/slots", response_model=SlotsResponse)
async def slots(
    request: SlotsRequest,
    settings: Settings = Depends(get_settings),
) -> SlotsResponse:
    try:
        found = find_slots(
            day=request.day,
            attendees=request.attendees,
            duration_min=request.duration_min,
            work_start=request.work_start or settings.work_start,
            work_end=request.work_end or settings.work_end,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return SlotsResponse(day=request.day, slots=found)
