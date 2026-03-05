"""
Round entity – represents a safari round in a Zone
"""

from __future__ import annotations
from typing import List, Optional
from utils.id_generator import generate_round_id

from datetime import datetime


class Round:
    """
    A Round is a time slot inside a specific Zone.
    Each round contains multiple trips created by Manager.
    """

    def __init__(self, zone: "Zone", start_time: datetime, end_time: datetime, price_per_seat: float):

        self.__round_id = generate_round_id()
        self.__zone = zone

        self.__start_time = start_time
        self.__end_time = end_time
        self.__price_per_seat = price_per_seat

        self.__trips: List["Trip"] = []   # trips belonging to this round

    # ─────────────────────────────
    # Properties
    # ─────────────────────────────

    @property
    def round_id(self):
        return self.__round_id

    @property
    def zone(self):
        return self.__zone

    @property
    def start_time(self):
        return self.__start_time

    @property
    def end_time(self):
        return self.__end_time

    @property
    def price_per_seat(self):
        return self.__price_per_seat

    @property
    def trips(self):
        return self.__trips

    # ─────────────────────────────
    # Availability Check
    # ─────────────────────────────

    def isAvailable(self, start: datetime, end: datetime) -> bool:
        """
        Check if the round time overlaps with requested time.
        """
        return (self.__start_time <= start <= self.__end_time) and (
            self.__start_time <= end <= self.__end_time
        )

    # ─────────────────────────────
    # Trip Management
    # ─────────────────────────────

    def createTrip(self, vehicle: "Vehicle", driver: "Driver") -> "Trip":
        """
        Manager creates a trip.
        Round → createTrip → returns Trip object
        """
        from .trip import Trip
        for other_round in self.zone.rounds:  # ต้องมี getter ของ rounds ใน Zone
            for t in other_round.trips:
                if t.driver.driver_id == driver.driver_id:
                # เช็คเวลาทับ
                    if not (self.end_time <= other_round.start_time or
                            self.start_time >= other_round.end_time):
                        raise ValueError("Driver is already assigned to another trip at this time")
                    
            # เช็ครถซ้ำ
        for other_round in self.zone.rounds:
            for t in other_round.trips:
                if t.vehicle.vehicle_id == vehicle.vehicle_id:
                    if not (self.end_time <= other_round.start_time or
                            self.start_time >= other_round.end_time):
                        raise ValueError("Vehicle is already assigned to another trip at this time")
                        
        trip = Trip(vehicle=vehicle, driver=driver, round_ref=self)
        self.__trips.append(trip)
        return trip

    def getTrip(self, trip_id: str) -> Optional["Trip"]:
        """
        Find trip by ID — used in booking sequence diagram
        """
        for t in self.__trips:
            if t.trip_id == trip_id:
                return t
        return None

    # ─────────────────────────────
    # Capacity Calculations
    # ─────────────────────────────

    def getTotalCapacity(self) -> int:
        """
        Sum of all vehicle capacities for all trips in this round
        """
        total = 0
        for t in self.__trips:
            total += t.total_seats
        return total

    def getCurrentVisitorCount(self) -> int:
        """
        Current visitors = sum(reserved seats of every trip)
        """
        count = 0
        for t in self.__trips:
            count += t.reserved_seats
        return count

    # ─────────────────────────────
    # Debug
    # ─────────────────────────────

    def __repr__(self):
        return (
            f"Round({self.__round_id}, zone={self.__zone.zone_id}, "
            f"trips={len(self.__trips)}, price={self.__price_per_seat})"
        )
