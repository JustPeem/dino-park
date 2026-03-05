from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trip import Trip
    from driver import Driver


class Vehicle:
    def __init__(self, vehicle_id: str, total_seats: int):
        self.__vehicle_id = vehicle_id
        self.__total_seats = total_seats
        self.__driver: "Driver | None" = None
        self.__trips: list["Trip"] = []

    # ── ใช้ภายนอก ─────────────────────────────────
    @property
    def vehicle_id(self) -> str:
        return self.__vehicle_id

    @property
    def total_seats(self) -> int:
        # ใช้ใน Trip.__init__ และ Round.get_total_capacity()
        return self.__total_seats
    
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
        return f"Vehicle(id={self.__vehicle_id}, seats={self.__total_seats})"