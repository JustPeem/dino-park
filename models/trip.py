from __future__ import annotations

from typing import TYPE_CHECKING

from utils.id_generator import id_gen

if TYPE_CHECKING:
    from .vehicle import Vehicle
    from .driver import Driver
    from .round import Round


class Trip:
    def __init__(self, vehicle: "Vehicle", driver: "Driver", round_ref: "Round", trip_id: str | None = None):
        self.__trip_id = trip_id or id_gen.trip_id()
        self.__vehicle = vehicle
        self.__driver = driver
        self.__round = round_ref
        self.__total_seats = vehicle.total_seats
        self.__reserved_seats = 0
        self.__checked_in_count = 0
        self.__status = "SCHEDULED"

    @property
    def trip_id(self):
        return self.__trip_id

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def driver(self):
        return self.__driver

    @driver.setter
    def driver(self, driver: "Driver") -> None:
        self.__driver = driver

    @property
    def round(self):
        return self.__round

    @property
    def start_time(self):
        return self.__round.start_time

    @property
    def end_time(self):
        return self.__round.end_time

    @property
    def total_seats(self):
        return self.__total_seats

    @property
    def reserved_seats(self):
        return self.__reserved_seats

    @property
    def status(self):
        return self.__status

    def check_seat_availability(self, seats: int) -> bool:
        return seats > 0 and (self.__reserved_seats + seats <= self.__total_seats)

    def reserve_seats(self, seats: int) -> bool:
        if not self.check_seat_availability(seats):
            return False
        self.__reserved_seats += seats
        return True

    def cancel_reservation(self, seats: int) -> None:
        self.__reserved_seats = max(0, self.__reserved_seats - seats)

    def increment_checked_in(self, count: int = 1) -> int:
        self.__checked_in_count = min(self.__reserved_seats, self.__checked_in_count + count)
        return self.__checked_in_count