# Staff (abstract), Manager, Ranger, TicketStaff, Driver

from abc import ABC
from typing import TYPE_CHECKING, Optional
from datetime import datetime, time, timedelta

if TYPE_CHECKING:
    from zone import Zone
    from trip import Trip
    from coupon import Coupon

VALID_SLOTS = [
    (time(9, 0),  time(12, 0)),
    (time(13, 0), time(16, 0)),
]
TRIP_DURATION = timedelta(hours=1)


def _validate_trip_time(start_time: datetime, end_time: datetime) -> None:
    """
    Validate that:
      1. Both inputs are datetime instances.
      2. start_time is not in the past.
      3. Duration is exactly 1 hour.
      4. Time falls within valid slots (09:00-12:00 or 13:00-16:00).
    Raises ValueError / TypeError if any condition is not met.
    """
    if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
        raise TypeError("start_time and end_time must be datetime instances.")
    if start_time >= end_time:
        raise ValueError("start_time must be before end_time.")
    if end_time - start_time != TRIP_DURATION:
        raise ValueError(
            f"Trip duration must be exactly 1 hour. Got {end_time - start_time}."
        )

    s = start_time.time()
    e = end_time.time()
    for slot_start, slot_end in VALID_SLOTS:
        if slot_start <= s and e <= slot_end:
            return

    raise ValueError(
        f"Trip time {s}–{e} is outside valid slots (09:00–12:00 or 13:00–16:00)."
    )


class Staff(ABC):
    """Abstract base class for all staff members."""

    def __init__(self, staff_id: int, name: str):
        if not isinstance(staff_id, int) or staff_id < 0:
            raise ValueError("staff_id must be a non-negative integer.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")

        self.__staff_id = staff_id
        self.__name = name.strip()

    @property
    def staff_id(self) -> int:
        return self.__staff_id

    @property
    def name(self) -> str:
        return self.__name

    def login(self) -> bool:
        """Authenticate staff member into the system."""
        print(f"Staff '{self.__name}' (ID: {self.__staff_id}) logged in.")
        return True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.__staff_id}, name={self.__name})"


class Manager(Staff):
    """Manager staff — handles notifications, approvals, and trip requests."""

    def __init__(self, staff_id: int, name: str):
        super().__init__(staff_id, name)

    def receive_food_low_notification(self, zone_id: int, food_type: str) -> None:
        """Receive a notification that food is running low in a zone."""
        if not isinstance(zone_id, int) or zone_id < 0:
            raise ValueError("zone_id must be a non-negative integer.")
        if not isinstance(food_type, str) or not food_type.strip():
            raise ValueError("food_type must be a non-empty string.")
        print(f"[Manager {self.name}] ALERT: Food '{food_type}' is low in Zone {zone_id}.")

    def approve_refill(self, zone_id: int) -> bool:
        """Approve a food refill request for a given zone."""
        if not isinstance(zone_id, int) or zone_id < 0:
            raise ValueError("zone_id must be a non-negative integer.")
        print(f"[Manager {self.name}] Approved refill for Zone {zone_id}.")
        return True

    def notify_refill_completed(self, zone_id: int) -> bool:
        """
        Receive notification that food refill is completed for a zone.
        Used in sequence: notifyRefillCompleted(zoneId) → acknowledged
        """
        if not isinstance(zone_id, int) or zone_id < 0:
            raise ValueError("zone_id must be a non-negative integer.")
        print(f"[Manager {self.name}] Refill completed acknowledged for Zone {zone_id}.")
        return True

    def request_create_trip(
        self,
        zone: "Zone",
        vehicle,
        driver: "Driver",
        start_time: datetime,
        end_time: datetime,
    ) -> Optional["Trip"]:
        """
        Request creation of a new trip for a zone.
        - Duration must be exactly 1 hour.
        - start_time must be within 09:00-12:00 or 13:00-16:00.
        Raises ValueError / TypeError if constraints are violated.
        """
        if zone is None:
            raise ValueError("zone must not be None.")
        if vehicle is None:
            raise ValueError("vehicle must not be None.")
        if driver is None:
            raise ValueError("driver must not be None.")

        _validate_trip_time(start_time, end_time)

        print(
            f"[Manager {self.name}] Requesting trip in Zone {zone.zone_id} "
            f"with Vehicle {vehicle.vehicle_id} and Driver {driver.staff_id} "
            f"from {start_time.strftime('%H:%M')} to {end_time.strftime('%H:%M')}."
        )
        return None

    def __repr__(self):
        return f"Manager(id={self.staff_id}, name={self.name})"


class Ranger(Staff):
    """Ranger staff — manages zones and dinosaur feeding."""

    def __init__(self, staff_id: int, name: str):
        super().__init__(staff_id, name)
        self.__zones: list["Zone"] = []

    @property
    def zones(self) -> list["Zone"]:
        return self.__zones

    def assign_zone(self, zone: "Zone") -> None:
        """Assign this ranger to a zone."""
        if zone is None:
            raise ValueError("zone must not be None.")
        if zone not in self.__zones:
            self.__zones.append(zone)
            print(f"[Ranger {self.name}] Assigned to Zone {zone.zone_id}.")

    def request_food_refill(self, zone_id: int, park) -> bool:
        """
        Request food refill for a zone via Park.
        Used in sequence: requestFoodRefill(zoneId) → Park → ... → Refill Success
        """
        if not isinstance(zone_id, int) or zone_id < 0:
            raise ValueError("zone_id must be a non-negative integer.")
        if park is None:
            raise ValueError("park must not be None.")
        print(f"[Ranger {self.name}] Requesting food refill for Zone {zone_id}.")
        return park.request_food_refill(zone_id)

    def request_refill(self, cage_id: int) -> None:
        """Request a food refill for a specific cage."""
        if not isinstance(cage_id, int) or cage_id < 0:
            raise ValueError("cage_id must be a non-negative integer.")
        print(f"[Ranger {self.name}] Requesting food refill for Cage {cage_id}.")

    def add_dino_lunch(self, cage_id: int) -> None:
        """Add lunch (food) to a specific dinosaur cage."""
        if not isinstance(cage_id, int) or cage_id < 0:
            raise ValueError("cage_id must be a non-negative integer.")
        print(f"[Ranger {self.name}] Adding lunch to Cage {cage_id}.")

    def __repr__(self):
        zone_ids = [z.zone_id for z in self.__zones]
        return f"Ranger(id={self.staff_id}, name={self.name}, zones={zone_ids})"


class TicketStaff(Staff):
    """Ticket staff — handles visitor check-in and coupon issuance."""

    def __init__(self, staff_id: int, name: str):
        super().__init__(staff_id, name)

    def check_in(self, ticket_id: str, park) -> bool:
        """
        Check in a visitor using their ticket ID.
        Delegates to the Park's check_in method.
        """
        if not isinstance(ticket_id, str) or not ticket_id.strip():
            raise ValueError("ticket_id must be a non-empty string.")
        if park is None:
            raise ValueError("park must not be None.")
        print(f"[TicketStaff {self.name}] Checking in ticket: {ticket_id}")
        return park.check_in(ticket_id)

    def add_food_coupon(self, member_id: str, park) -> str:
        """
        Issue a food coupon to a member after their visit.
        Delegates to Park.issue_food_coupon(member_id).
        Used in sequence: addFoodCoupon(memberId) → Park → Member → Ticket → Coupon
        """
        if not isinstance(member_id, str) or not member_id.strip():
            raise ValueError("member_id must be a non-empty string.")
        if park is None:
            raise ValueError("park must not be None.")
        print(f"[TicketStaff {self.name}] Issuing food coupon for Member {member_id}.")
        return park.issue_food_coupon(member_id)

    def __repr__(self):
        return f"TicketStaff(id={self.staff_id}, name={self.name})"


class Driver(Staff):
    """Driver staff — drives vehicles on trips."""

    def __init__(self, staff_id: int, name: str, license_id: int):
        super().__init__(staff_id, name)
        if not isinstance(license_id, int) or license_id < 0:
            raise ValueError("license_id must be a non-negative integer.")
        self.__license_id = license_id
        self.__trips: list["Trip"] = []

    @property
    def license_id(self) -> int:
        return self.__license_id

    @property
    def trips(self) -> list["Trip"]:
        return self.__trips

    def is_available(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Check whether the driver has no conflicting trips in the given time range.
        Returns True if the driver is free.
        """
        if not isinstance(start_time, datetime) or not isinstance(end_time, datetime):
            raise TypeError("start_time and end_time must be datetime instances.")
        if start_time >= end_time:
            raise ValueError("start_time must be before end_time.")
        for trip in self.__trips:
            if not (end_time <= trip.start_time or start_time >= trip.end_time):
                return False
        return True

    def add_trip(self, trip: "Trip") -> None:
        """Assign a trip to this driver."""
        if trip is None:
            raise ValueError("trip must not be None.")
        if trip not in self.__trips:
            self.__trips.append(trip)
            print(f"[Driver {self.name}] Assigned to Trip {trip.trip_id}.")

    def __repr__(self):
        return (
            f"Driver(id={self.staff_id}, name={self.name}, "
            f"license={self.__license_id}, trips={len(self.__trips)})"
        )