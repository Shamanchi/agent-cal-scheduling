"""Поиск общих свободных слотов: математика интервалов, без сети."""

from __future__ import annotations

from datetime import datetime, timedelta

from pydantic import BaseModel

DATETIME_FMT = "%Y-%m-%dT%H:%M"
DATE_FMT = "%Y-%m-%d"
TIME_FMT = "%H:%M"


class BusyInterval(BaseModel):
    start: str
    end: str


class Attendee(BaseModel):
    name: str
    busy: list[BusyInterval] = []


class FreeSlot(BaseModel):
    start: str
    end: str


def _parse_dt(value: str) -> datetime:
    try:
        return datetime.strptime(value, DATETIME_FMT)
    except ValueError as exc:
        raise ValueError(f"datetime must be YYYY-MM-DDTHH:MM, got {value!r}") from exc


def _parse_day(value: str) -> str:
    try:
        datetime.strptime(value, DATE_FMT)
    except ValueError as exc:
        raise ValueError(f"day must be YYYY-MM-DD, got {value!r}") from exc
    return value


def _parse_time(value: str) -> tuple[int, int]:
    try:
        hour, minute = (int(part) for part in value.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except (ValueError, TypeError) as exc:
        raise ValueError(f"time must be HH:MM, got {value!r}") from exc
    return hour, minute


def find_slots(
    day: str,
    attendees: list[Attendee],
    duration_min: int,
    work_start: str = "09:00",
    work_end: str = "18:00",
) -> list[FreeSlot]:
    """Вернуть свободные окна в рабочий день, достаточные для встречи."""
    if duration_min < 1:
        raise ValueError("duration_min must be >= 1")
    day = _parse_day(day)
    start_hour, start_minute = _parse_time(work_start)
    end_hour, end_minute = _parse_time(work_end)
    window_start = datetime.strptime(f"{day}T{start_hour:02d}:{start_minute:02d}", DATETIME_FMT)
    window_end = datetime.strptime(f"{day}T{end_hour:02d}:{end_minute:02d}", DATETIME_FMT)
    if window_end <= window_start:
        raise ValueError("work_end must be after work_start")

    busy: list[tuple[datetime, datetime]] = []
    for attendee in attendees:
        for interval in attendee.busy:
            start = _parse_dt(interval.start)
            end = _parse_dt(interval.end)
            if end <= start:
                raise ValueError(f"busy interval end must be after start: {interval}")
            clipped_start = max(start, window_start)
            clipped_end = min(end, window_end)
            if clipped_end > clipped_start:
                busy.append((clipped_start, clipped_end))
    busy.sort()
    merged: list[list[datetime]] = []
    for start, end in busy:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])

    slots: list[FreeSlot] = []
    cursor = window_start
    needed = timedelta(minutes=duration_min)
    for start, end in merged:
        if start - cursor >= needed:
            slots.append(
                FreeSlot(
                    start=cursor.strftime(DATETIME_FMT),
                    end=start.strftime(DATETIME_FMT),
                )
            )
        cursor = max(cursor, end)
    if window_end - cursor >= needed:
        slots.append(
            FreeSlot(start=cursor.strftime(DATETIME_FMT), end=window_end.strftime(DATETIME_FMT))
        )
    return slots
