"""Unit-тесты планировщика: без сети, детерминированы."""

import pytest

from app.services.scheduler import Attendee, BusyInterval, find_slots


def _ann_bob() -> list[Attendee]:
    return [
        Attendee(
            name="Ann",
            busy=[BusyInterval(start="2026-09-22T10:00", end="2026-09-22T11:00")],
        ),
        Attendee(
            name="Bob",
            busy=[BusyInterval(start="2026-09-22T10:30", end="2026-09-22T12:00")],
        ),
    ]


def test_common_free_slots() -> None:
    slots = find_slots("2026-09-22", _ann_bob(), duration_min=30)
    assert [(s.start, s.end) for s in slots] == [
        ("2026-09-22T09:00", "2026-09-22T10:00"),
        ("2026-09-22T12:00", "2026-09-22T18:00"),
    ]


def test_too_long_meeting_no_slots() -> None:
    slots = find_slots("2026-09-22", _ann_bob(), duration_min=400)
    assert slots == []


def test_fully_busy_day() -> None:
    busy = [
        Attendee(
            name="Ann",
            busy=[BusyInterval(start="2026-09-22T09:00", end="2026-09-22T18:00")],
        )
    ]
    assert find_slots("2026-09-22", busy, duration_min=15) == []


def test_outside_window_ignored() -> None:
    busy = [
        Attendee(
            name="Ann",
            busy=[BusyInterval(start="2026-09-22T19:00", end="2026-09-22T20:00")],
        )
    ]
    slots = find_slots("2026-09-22", busy, duration_min=60)
    assert len(slots) == 1
    assert slots[0].start == "2026-09-22T09:00"


def test_bad_input_rejected() -> None:
    with pytest.raises(ValueError):
        find_slots("22.09.2026", [], duration_min=30)
    with pytest.raises(ValueError):
        find_slots("2026-09-22", [], duration_min=0)
    with pytest.raises(ValueError):
        find_slots(
            "2026-09-22",
            [Attendee(name="Ann", busy=[BusyInterval(start="2026-09-22T12:00", end="2026-09-22T11:00")])],
            duration_min=30,
        )
