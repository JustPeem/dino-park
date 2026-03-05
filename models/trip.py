"""
models/trip.py
Trip entity – represents a safari vehicle trip
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from utils.id_generator import generate_trip_id

if TYPE_CHECKING:
    from .vehicle import Vehicle
    from .driver import Driver


class Trip:
    """
    Represents a safari vehicle trip
    """

    def __init__(self, vehicle: "Vehicle", driver: "Driver"):

        # สร้าง trip id
        self.__trip_id = generate_trip_id()

        # ความสัมพันธ์กับ Vehicle และ Driver
        self.__vehicle = vehicle
        self.__driver = driver

        # ดึงจำนวนที่นั่งจากรถ
        self.__total_seats = vehicle.seat_capacity

        # สถานะที่นั่ง
        self.__reserved_seats = 0
        self.__checked_in_count = 0

        # สถานะ trip
        self.__status = "SCHEDULED"  # SCHEDULED → IN_PROGRESS → COMPLETED

    # ─────────────────────
    # Properties
    # ─────────────────────

    @property
    def trip_id(self) -> str:
        return self.__trip_id

    @property
    def vehicle(self) -> "Vehicle":
        return self.__vehicle

    @property
    def driver(self) -> "Driver":
        return self.__driver

    @property
    def total_seats(self) -> int:
        return self.__total_seats

    @property
    def reserved_seats(self) -> int:
        return self.__reserved_seats

    @property
    def checked_in_count(self) -> int:
        return self.__checked_in_count

    @property
    def status(self) -> str:
        return self.__status

    # ─────────────────────
    # Seat Management
    # ─────────────────────

    def check_seat_availability(self, seats: int) -> bool:
        """
        Check if enough seats remain
        """
        available = self.__total_seats - self.__reserved_seats
        return seats <= available

    def reserve_seats(self, seats: int) -> bool:
        """
        Reserve seats for booking
        """
        if not self.check_seat_availability(seats):
            return False

        self.__reserved_seats += seats
        return True

    def cancel_reservation(self, seats: int) -> None:
        """
        Cancel seat reservation
        """
        self.__reserved_seats -= seats

        if self.__reserved_seats < 0:
            self.__reserved_seats = 0

    # ─────────────────────
    # Check-in
    # ─────────────────────

    def increment_checked_in(self, count: int = 1) -> None:
        """
        Increase number of checked-in passengers
        """
        self.__checked_in_count += count

        if self.__checked_in_count > self.__reserved_seats:
            self.__checked_in_count = self.__reserved_seats

    # ─────────────────────
    # Trip Lifecycle
    # ─────────────────────

    def start_trip(self) -> None:
        """
        Start the safari trip
        """
        self.__status = "IN_PROGRESS"

    def end_trip(self) -> None:
        """
        End the safari trip
        """
        self.__status = "COMPLETED"

    # ─────────────────────
    # Debug
    # ─────────────────────

    def __repr__(self) -> str:
        return (
            f"Trip({self.__trip_id}, "
            f"reserved={self.__reserved_seats}/{self.__total_seats}, "
            f"checked_in={self.__checked_in_count}, "
            f"status={self.__status})"
        )