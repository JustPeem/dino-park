from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trip import Trip


class Driver:
    def __init__(self, staff_id: str, name: str, license_id: str):
        self.__staff_id = staff_id
        self.__name = name
        self.__license_id = license_id
        self.__trips: list["Trip"] = []

    # ── ใช้ภายนอก (park.py get_driver) ──────────
    @property
    def license_id(self) -> str:
        return self.__license_id

    def login(self) -> bool:
        return True

    # ── SD2: isAvailable(startTime, endTime) ──────
    def is_available(self, start: datetime, end: datetime) -> bool:
        for trip in self.__trips:
            if trip.status == "CANCELLED":
                continue
            round_obj = trip.round
            if round_obj is None:
                continue
            if not (end <= round_obj.start_time or start >= round_obj.end_time):
                return False
        return True

    # ── SD2: addTrip(trip) ────────────────────────
    def add_trip(self, trip: "Trip") -> None:
        self.__trips.append(trip)

    def __repr__(self) -> str:
        return f"Driver(id={self.__staff_id}, name={self.__name!r}, license={self.__license_id})"