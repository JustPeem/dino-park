from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .trip import Trip


class Driver:
    def __init__(self, staff_id: str, name: str, license_id: str):
        self.__staff_id = staff_id
        self.__name = name
        self.__license_id = license_id
        self.__trips: list["Trip"] = []

    @property
    def license_id(self) -> str:
        return self.__license_id

    @property
    def staff_id(self) -> str:
        return self.__staff_id

    def login(self) -> bool:
        return True

    def is_available(self, start: datetime, end: datetime) -> bool:
        for trip in self.__trips:
            if not (end <= trip.start_time or start >= trip.end_time):
                return False
        return True

    def add_trip(self, trip: "Trip") -> None:
        if trip not in self.__trips:
            self.__trips.append(trip)

    def __repr__(self) -> str:
        return f"Driver(id={self.__staff_id}, name={self.__name!r}, license={self.__license_id})"