"""
Trip entity – represents a safari vehicle trip (with error handling)
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from utils.id_generator import generate_trip_id

if TYPE_CHECKING:
    from .vehicle import Vehicle
    from .driver import Driver
    from .round import Round


class Trip:
    """
    Represents a safari trip with vehicle, driver, round + seat control
    """

    def __init__(self, vehicle: "Vehicle", driver: "Driver", round_ref: "Round"):

        self.__trip_id = generate_trip_id()

        # relationships
        self.__vehicle = vehicle
        self.__driver = driver
        self.__round = round_ref

        # seats
        self.__total_seats = vehicle.seat_capacity
        self.__reserved_seats = 0
        self.__checked_in_count = 0

        # lifecycle
        self.__status = "SCHEDULED"

        # register
        vehicle.add_trip(self)
        driver.add_trip(self)

    # ───────────────────────────
    # Properties
    # ───────────────────────────

    @property
    def trip_id(self):
        return self.__trip_id

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def driver(self):
        return self.__driver

    @property
    def round(self):
        return self.__round

    @property
    def total_seats(self):
        return self.__total_seats

    @property
    def reserved_seats(self):
        return self.__reserved_seats

    @property
    def checked_in_count(self):
        return self.__checked_in_count

    @property
    def status(self):
        return self.__status

    # ───────────────────────────
    # SEAT MANAGEMENT WITH ERRORS
    # ───────────────────────────

    def check_seat_availability(self, seats: int) -> bool:
        """
        Check if enough seats remain
        """
        if seats <= 0:
            raise ValueError("Seat number must be greater than 0")

        available = self.__total_seats - self.__reserved_seats
        return seats <= available

    def reserve_seats(self, seats: int) -> bool:
        """
        Reserve seats with error handling
        """
        if seats > self.total_seats:
            raise ValueError("It over total seat")
        
        if seats <= 0:
            raise ValueError("Invalid seat number: must be > 0")

        if self.__reserved_seats >= self.__total_seats:
            raise Exception("Reserve failed: seats are full")

        if not self.check_seat_availability(seats):
            raise Exception("Reserve failed: not enough seats available")

        self.__reserved_seats += seats
        return True

    def cancel_reservation(self, seats: int) -> None:
        if seats <= 0:
            raise ValueError("Invalid seat number")

        self.__reserved_seats -= seats
        if self.__reserved_seats < 0:
            self.__reserved_seats = 0

    # ───────────────────────────
    # CHECK-IN
    # ───────────────────────────

    def increment_checked_in(self, count: int = 1) -> None:

        if count <= 0:
            raise ValueError("Invalid check-in count")

        if self.__checked_in_count + count > self.__reserved_seats:
            raise Exception("Check-in failed: exceeds reserved seats")

        self.__checked_in_count += count

    # ───────────────────────────
    # TRIP STATE
    # ───────────────────────────

    def start_trip(self):
        if self.__status != "SCHEDULED":
            raise Exception("Trip cannot start: invalid state")

        self.__status = "IN_PROGRESS"

    def end_trip(self):
        if self.__status != "IN_PROGRESS":
            raise Exception("Trip cannot end: trip not started")

        self.__status = "COMPLETED"

    # ───────────────────────────
    # DEBUG
    # ───────────────────────────

    def __repr__(self):
        return (
            f"Trip({self.__trip_id}, round={self.__round.round_id}, "
            f"reserved={self.__reserved_seats}/{self.__total_seats}, "
            f"checked_in={self.__checked_in_count}, status={self.__status})"
        )
