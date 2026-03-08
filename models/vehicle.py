from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .trip import Trip


class Vehicle:
    def __init__(self, vehicle_id: str, total_seats: int):
        self.__vehicle_id = vehicle_id
        self.__total_seats = total_seats
        self.__trips: list["Trip"] = []

    @property
    def vehicle_id(self) -> str:
        return self.__vehicle_id

    @property
    def total_seats(self) -> int:
        return self.__total_seats

    def is_available(self, start: datetime, end: datetime) -> bool:
        for trip in self.__trips:
            if not (end <= trip.start_time or start >= trip.end_time):
                return False
        return True

    def add_trip(self, trip: "Trip") -> None:
        if trip not in self.__trips:
            self.__trips.append(trip)

    def __repr__(self) -> str:
        return f"Vehicle(id={self.__vehicle_id}, seats={self.__total_seats})"