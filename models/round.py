from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .trip import Trip
    from .vehicle import Vehicle
    from .driver import Driver
    from .zone import Zone


class Round:
    def __init__(
        self,
        zone: "Zone",
        start_time: datetime,
        end_time: datetime,
        price_per_seat: float,
        round_id: str | None = None,
    ):
        self.__round_id = round_id or f"R-{start_time.strftime('%Y%m%d%H%M')}"
        self.__zone = zone
        self.__start_time = start_time
        self.__end_time = end_time
        self.__price_per_seat = price_per_seat
        self.__trips: list["Trip"] = []

    @property
    def round_id(self) -> str:
        return self.__round_id

    @property
    def date(self):
        return self.__start_time.date()

    @property
    def start_time(self) -> datetime:
        return self.__start_time

    @property
    def end_time(self) -> datetime:
        return self.__end_time

    @property
    def price_per_seat(self) -> float:
        return self.__price_per_seat

    @property
    def trips(self) -> list["Trip"]:
        return self.__trips

    def is_available(self, start: datetime | None, end: datetime | None) -> bool:
        if start is None or end is None:
            return self.__end_time > datetime.now()
        return self.__start_time <= start and end <= self.__end_time

    def create_trip(self, vehicle: "Vehicle", driver: "Driver", trip_id: str | None = None) -> "Trip":
        from .trip import Trip

        trip = Trip(vehicle=vehicle, driver=driver, round_ref=self, trip_id=trip_id)
        self.__trips.append(trip)
        return trip

    def get_trip(self, trip_id: str) -> Optional["Trip"]:
        for trip in self.__trips:
            if trip.trip_id == trip_id:
                return trip
        return None

    def get_total_capacity(self) -> int:
        return sum(t.total_seats for t in self.__trips)

    def get_current_visitor_count(self) -> int:
        return sum(t.reserved_seats for t in self.__trips)

    # backward compatible aliases
    def isAvailable(self, start: datetime, end: datetime) -> bool:
        return self.is_available(start, end)

    def createTrip(self, vehicle: "Vehicle", driver: "Driver") -> "Trip":
        return self.create_trip(vehicle, driver)

    def getTrip(self, trip_id: str) -> Optional["Trip"]:
        return self.get_trip(trip_id)

    def getTotalCapacity(self) -> int:
        return self.get_total_capacity()

    def getCurrentVisitorCount(self) -> int:
        return self.get_current_visitor_count()
