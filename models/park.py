from __future__ import annotations
from datetime import datetime, date
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from zone import Zone
    from vehicle import Vehicle
    from driver import Driver
    from booking import Booking
    from member import Member
    from payment import Payment
    from user import User


class Park:
    def __init__(self, name: str):
        self.__name = name
        self.__staff: list = []
        self.__members: list["Member"] = []
        self.__payments: list["Payment"] = []
        self.__zones: list["Zone"] = []
        self.__bookings: list["Booking"] = []
        self.__vehicles: list["Vehicle"] = []

    # ── Zone helpers ──────────────────────────────────────────────────────
    def add_zone(self, zone: "Zone") -> None:
        self.__zones.append(zone)

    def get_zone(self, zone_id: str) -> Optional["Zone"]:
        for z in self.__zones:
            if z.zone_id == zone_id:
                return z
        return None

    # ── Vehicle helpers ───────────────────────────────────────────────────
    def add_vehicle(self, vehicle: "Vehicle") -> None:
        self.__vehicles.append(vehicle)

    def get_vehicle(self, vehicle_id: str) -> Optional["Vehicle"]:
        for v in self.__vehicles:
            if v.vehicle_id == vehicle_id:
                return v
        return None

    # ── Driver helpers ────────────────────────────────────────────────────
    def add_staff(self, staff) -> None:
        self.__staff.append(staff)

    def get_driver(self, driver_key: str) -> Optional["Driver"]:
        from driver import Driver
        for s in self.__staff:
            if isinstance(s, Driver) and s.license_id == driver_key:
                return s
        return None

    # ── Member helpers ────────────────────────────────────────────────────
    def add_member(self, member: "Member") -> None:
        self.__members.append(member)

    def find_member_by_phone_number(self, number: str) -> Optional["Member"]:
        for m in self.__members:
            if m.phone_number == number:
                return m
        return None

    # ── User / Booking helpers ────────────────────────────────────────────
    def get_user_by_id(self, user_id: str) -> Optional["User"]:
        for m in self.__members:
            if m.user_id == user_id:
                return m
        return None

    def add_booking(self, booking: "Booking") -> None:
        self.__bookings.append(booking)

    def get_booking(self, booking_id: str) -> Optional["Booking"]:
        for b in self.__bookings:
            if b.booking_id == booking_id:
                return b
        return None

    def find_booking_by_ticket(self, ticket_id: str) -> Optional["Booking"]:
        for b in self.__bookings:
            if b.get_ticket(ticket_id) is not None:
                return b
        return None

    # ── Visitor stats ─────────────────────────────────────────────────────
    def get_daily_visitor_count(self, query_date: date) -> int:
        count = 0
        for b in self.__bookings:
            if b.booking_date.date() == query_date and b.status == "CONFIRMED":
                count += len(b.tickets)
        return count

    # ── Trip creation  (Manager → SD2) ───────────────────────────────────
    def create_trip(self, zone_id: str, vehicle_key: str, driver_key: str,
                    start_time: datetime, end_time: datetime) -> dict:
        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        round_obj = zone.check_round(start_time, end_time)
        if round_obj is None:
            return {"status": "error", "message": "Zone round full"}

        vehicle = self.get_vehicle(vehicle_key)
        if vehicle is None:
            return {"status": "error", "message": "Vehicle not found"}
        if not vehicle.is_available(start_time, end_time):
            return {"status": "error", "message": "Vehicle not available"}

        driver = self.get_driver(driver_key)
        if driver is None:
            return {"status": "error", "message": "Driver not found"}
        if not driver.is_available(start_time, end_time):
            return {"status": "error", "message": "Driver not available"}

        trip = round_obj.create_trip(vehicle)
        trip.driver = driver
        vehicle.add_trip(trip)
        driver.add_trip(trip)

        return {"status": "success", "trip": trip}

    # ── Food / Dino helpers  (Ranger → SD1) ──────────────────────────────
    def request_food_refill(self, zone_id: str) -> dict:
        """
        SD1: Ranger → Park → Zone.getCages() → Cage.getDinos()
             → Dino.getFoodSource() → Cage.addFood()
             → Park.notifyRefillCompleted()
        """
        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        for cage in zone.get_cages():
            for dino in cage.get_dinos():
                cage.add_food(dino.food_source)

        # SD1: notifyRefillCompleted(zoneId)
        self.notify_refill_completed(zone_id)
        return {"status": "success", "message": "Refill Success"}

    def notify_refill_completed(self, zone_id: str) -> None:
        """SD1: Park → Ranger: notifyRefillCompleted(zoneId)"""
        print(f"[Notification] Zone {zone_id}: Food refill completed.")

    # ── Booking flow  (Visitor → SD5) ────────────────────────────────────
    def book_trip(self, user_id: str, zone_id: str, round_id: str,  # str ทั้งหมด
                  trip_id: str, seats: int, base_price: float) -> dict:
        from booking import Booking

        # Business Rule: 1–10 seats per booking
        if seats < 1 or seats > 10:
            return {"status": "error",
                    "message": "Seats must be between 1 and 10 per booking"}

        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        round_obj = zone.get_round(round_id)   # str ตาม zone.get_round(str)
        if round_obj is None:
            return {"status": "error", "message": "Round not found"}

        # Business Rule: max 30 days advance booking
        days_ahead = (round_obj.date - date.today()).days
        if days_ahead > 30:
            return {"status": "error",
                    "message": "Cannot book more than 30 days in advance"}
        if days_ahead < 0:
            return {"status": "error", "message": "Cannot book a past round"}

        trip = round_obj.get_trip(trip_id)
        if trip is None:
            return {"status": "error", "message": "Trip not found"}

        if not trip.check_seat_availability(seats):
            return {"status": "error", "message": "Not enough seats"}

        trip.reserve_seats(seats)
        user = self.get_user_by_id(user_id)

        booking = Booking()
        booking.create_booking(user, round_obj, trip, seats, base_price)
        self.add_booking(booking)

        return {"status": "success", "booking_id": booking.booking_id, "booking": booking}

    # ── Payment flow  (Visitor → SD6) ────────────────────────────────────
    def process_payment(self, booking_id: str, phone_number: str,
                        coupon_code: Optional[str] = None) -> dict:
        booking = self.get_booking(booking_id)
        if booking is None:
            return {"status": "error", "message": "Booking not found"}

        base_price = booking.base_price
        member = self.find_member_by_phone_number(phone_number)

        discount = 0.0
        if member and coupon_code:
            discount = member.use_coupon(coupon_code, base_price)

        booking.calculate_final_price(discount)
        result = booking.create_payment()

        if result:
            booking.confirm_booking()
            tickets = booking.create_ticket()
            return {"status": "success", "tickets": tickets}
        return {"status": "error", "message": "Payment failed"}

    # ── Cancel booking  (Visitor → SD7) ──────────────────────────────────
    def cancel_booking(self, booking_id: str) -> dict:
        booking = self.get_booking(booking_id)
        if booking is None:
            return {"status": "error", "message": "Booking not found"}

        trip_start: Optional[datetime] = None
        if booking.trip:
            trip_start = booking.trip.start_time

        success = booking.cancel_booking(booking_id, trip_start)
        if success:
            return {"status": "success", "message": "Booking cancelled"}
        return {"status": "error", "message": "Cancel failed"}

    # ── Check-in  (TicketStaff → SD8) ────────────────────────────────────
    def check_in(self, ticket_id: str) -> dict:
        booking = self.find_booking_by_ticket(ticket_id)
        if booking is None:
            return {"status": "error", "message": "Booking Not Found"}

        if not booking.is_confirmed():
            return {"status": "error", "message": "Booking Not Confirmed"}

        ticket = booking.get_ticket(ticket_id)
        if ticket is None:
            return {"status": "error", "message": "Ticket not found"}

        if ticket.is_used:
            return {"status": "error", "message": "Ticket Already Used"}

        ticket.set_used(True)

        checked_in_count = None
        trip = booking.trip
        if trip:
            checked_in_count = trip.increment_checked_in()

        return {"status": "success", "message": "Check-in Success",
                "checked_in_count": checked_in_count}

    # ── Food coupon  (TicketStaff → SD3) ─────────────────────────────────
    def issue_food_coupon(self, member_id: str) -> dict:
        from coupon import Coupon
        from datetime import timedelta

        member = None
        for m in self.__members:
            if m.user_id == member_id:
                member = m
                break

        if member is None:
            return {"status": "error", "message": "Member not found"}

        existing = member.get_active_food_coupon()
        if existing is not None:
            if not existing.is_used and existing.expiry_date > datetime.now():
                return {"status": "error", "message": "Already has active coupon"}

        expiry = datetime.now() + timedelta(days=30)
        new_coupon = Coupon.create("FOOD_COUPON", 50.0, expiry)
        member.add_coupon(new_coupon)
        return {"status": "success", "message": "Coupon issued successfully",
                "coupon": new_coupon}

    # ── Check available seats  (Member → SD4) ────────────────────────────
    def check_available_seats(self, zone_id: str, round_id: str) -> dict:  # str
        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        if not zone.check_availability(None, None):
            return {"status": "error", "message": "Zone is not available"}

        round_obj = zone.get_round(round_id)   # str ตาม zone.get_round(str)
        if round_obj is None:
            return {"status": "error", "message": "Round not found"}

        if not round_obj.is_available(None, None):
            return {"status": "error", "message": "Round has already ended"}

        capacity = round_obj.get_total_capacity()
        current = round_obj.get_current_visitor_count()
        available = capacity - current

        if available <= 0:
            return {"status": "error", "message": "No seats available"}

        return {"status": "success", "available_seats": available}

    def __repr__(self) -> str:
        return f"Park(name={self.__name!r})"