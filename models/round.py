from datetime import datetime, date
from typing import List, Optional

from .trip import Trip
from utils.id_generator import generate_trip_id


class Round:

    def __init__(
        self,round_id: int,start_time: datetime,end_time: datetime, date: date,zone):
        self.__round_id = round_id
        self.__start_time = start_time
        self.__end_time = end_time
        self.__date = date
        self.__zone = zone
        self.__trips: List[Trip] = []


    @property
    def round_id(self) -> str:
        return self.__round_id


    @property
    def date(self) -> date:
        return self.__date


    @property
    def start_time(self) -> datetime:
        return self.__start_time


    @property
    def end_time(self) -> datetime:
        return self.__end_time

    # -----------------------------
    # createTrip(Vehicle vehicle)
    # -----------------------------
    def create_trip(self, vehicle) -> Trip:

        trip = Trip(trip_id=generate_trip_id(),vehicle=vehicle)

        self.__trips.append(trip)
        return trip

    # -----------------------------
    # isAvailable(start,end)
    # -----------------------------
    def is_available(self, start: datetime, end: datetime) -> bool:

        if start >= self.__start_time and end <= self.__end_time:
            return True

        return False

    # -----------------------------
    # getTotalCapacity()
    # -----------------------------
    def get_total_capacity(self) -> int:

        total = 0
        for trip in self.__trips:
            total += trip.total_seats

        return total

    # -----------------------------
    # getCurrentVisitorCount()
    # -----------------------------
    def get_current_visitor_count(self) -> int:

        total = 0
        for trip in self.__trips:
            total += trip.used_seats

        return total

    # -----------------------------
    # getTrip(tripId)
    # -----------------------------
    def get_trip(self, trip_id: str) -> Optional[Trip]:

        for trip in self.__trips:
            if trip.trip_id == trip_id:
                return trip

        return None