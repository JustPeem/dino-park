from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING, Optional

from .payment import CashPayment, QRPayment

if TYPE_CHECKING:
    from .zone import Zone
    from .vehicle import Vehicle
    from .driver import Driver
    from .booking import Booking
    from .users import Member, User


class Park:
    def __init__(self, name: str):
        self.__name = name
        self.__staff: list = []
        self.__members: list["Member"] = []
        self.__zones: list["Zone"] = []
        self.__bookings: list["Booking"] = []
        self.__vehicles: list["Vehicle"] = []

    @property
    def zones(self) -> list["Zone"]:
        return self.__zones

    def add_zone(self, zone: "Zone") -> None:
        self.__zones.append(zone)

    def get_zone(self, zone_id: str) -> Optional["Zone"]:
        return next((z for z in self.__zones if z.zone_id == zone_id), None)

    def add_vehicle(self, vehicle: "Vehicle") -> None:
        self.__vehicles.append(vehicle)

    def get_vehicle(self, vehicle_id: str) -> Optional["Vehicle"]:
        return next((v for v in self.__vehicles if v.vehicle_id == vehicle_id), None)

    def add_staff(self, staff) -> None:
        self.__staff.append(staff)

    def get_driver(self, driver_key: str) -> Optional["Driver"]:
        from .driver import Driver

        return next((s for s in self.__staff if isinstance(s, Driver) and s.license_id == driver_key), None)

    def add_member(self, member: "Member") -> None:
        self.__members.append(member)

    def find_member_by_phone_number(self, number: str) -> Optional["Member"]:
        return next((m for m in self.__members if m.phone_number == number), None)

    def get_user_by_id(self, user_id: str) -> Optional["User"]:
        return next((m for m in self.__members if m.user_id == user_id), None)

    def add_booking(self, booking: "Booking") -> None:
        self.__bookings.append(booking)

    def get_booking(self, booking_id: str) -> Optional["Booking"]:
        return next((b for b in self.__bookings if b.booking_id == booking_id), None)

    def find_booking_by_ticket(self, ticket_id: str) -> Optional["Booking"]:
        return next((b for b in self.__bookings if b.get_ticket(ticket_id) is not None), None)

    def get_daily_visitor_count(self, query_date: date) -> int:
        return sum(len(b.tickets) for b in self.__bookings if b.booking_date.date() == query_date and b.status == "CONFIRMED")

    def create_trip(self, zone_id: str, vehicle_key: str, driver_key: str, start_time: datetime, end_time: datetime) -> dict:
        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        round_obj = zone.check_round(start_time, end_time)
        if round_obj is None:
            return {"status": "error", "message": "Zone round full"}

        vehicle = self.get_vehicle(vehicle_key)
        if vehicle is None or not vehicle.is_available(start_time, end_time):
            return {"status": "error", "message": "Vehicle not available"}

        driver = self.get_driver(driver_key)
        if driver is None or not driver.is_available(start_time, end_time):
            return {"status": "error", "message": "Driver not available"}

        trip = round_obj.create_trip(vehicle, driver)
        vehicle.add_trip(trip)
        driver.add_trip(trip)
        return {"status": "success", "trip": trip}

    def request_food_refill(self, zone_id: str) -> dict:
        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        for cage in zone.get_cages():
            for dino in cage.get_dinos():
                cage.add_food(dino.food_source)
        return {"status": "success", "message": "Refill Success"}

    def book_trip(self, user_id: str, zone_id: str, round_id: str, trip_id: str, seats: int, base_price: float) -> dict:
        from .booking import Booking

        if seats < 1 or seats > 10:
            return {"status": "error", "message": "Seats must be between 1 and 10 per booking"}

        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        round_obj = zone.get_round(round_id)
        if round_obj is None:
            return {"status": "error", "message": "Round not found"}

        days_ahead = (round_obj.date - date.today()).days
        if days_ahead > 30 or days_ahead < 0:
            return {"status": "error", "message": "Round date is out of booking window"}

        trip = round_obj.get_trip(trip_id)
        if trip is None or not trip.reserve_seats(seats):
            return {"status": "error", "message": "Not enough seats"}

        user = self.get_user_by_id(user_id)
        if user is None:
            return {"status": "error", "message": "User not found"}

        booking = Booking(user, round_obj, trip, seats, base_price)
        self.add_booking(booking)
        return {"status": "success", "booking_id": booking.booking_id, "booking": booking}

    def process_payment(self, booking_id: str, phone_number: str, coupon_code: Optional[str] = None, payment_channel: str = "cash") -> dict:
        booking = self.get_booking(booking_id)
        if booking is None:
            return {"status": "error", "message": "Booking not found"}

        member = self.find_member_by_phone_number(phone_number)
        member_discount = member.member_discount_percent() if member else 0.0
        coupon_discount = member.use_coupon(coupon_code) if (member and coupon_code) else 0.0

        booking.calculate_final_price(member_discount, coupon_discount)

        method = QRPayment() if payment_channel.lower() == "qr" else CashPayment()
        payment = booking.create_payment(method)
        if payment.pay():
            tickets = booking.confirm_booking()
            return {"status": "success", "tickets": tickets}
        return {"status": "error", "message": "Payment failed"}

    def cancel_booking(self, booking_id: str) -> dict:
        booking = self.get_booking(booking_id)
        if booking is None:
            return {"status": "error", "message": "Booking not found"}

        trip_start: Optional[datetime] = booking.trip.start_time if booking.trip else None
        if booking.cancel_booking(booking_id, trip_start):
            return {"status": "success", "message": "Booking cancelled"}
        return {"status": "error", "message": "Cancel failed"}

    def check_in(self, ticket_id: str) -> dict:
        booking = self.find_booking_by_ticket(ticket_id)
        if booking is None or not booking.is_confirmed():
            return {"status": "error", "message": "Booking Not Confirmed"}

        ticket = booking.get_ticket(ticket_id)
        if ticket is None or ticket.is_used:
            return {"status": "error", "message": "Ticket invalid"}

        ticket.set_used(True)
        checked_in_count = booking.trip.increment_checked_in() if booking.trip else 0
        return {"status": "success", "checked_in_count": checked_in_count}

    def issue_food_coupon(self, member_id: str) -> dict:
        from .coupon import Coupon

        member = self.get_user_by_id(member_id)
        if member is None:
            return {"status": "error", "message": "Member not found"}

        existing = member.get_active_food_coupon()
        if existing is not None:
            return {"status": "error", "message": "Already has active coupon"}

        expiry = datetime.now() + timedelta(days=30)
        new_coupon = Coupon.create("FOOD_COUPON", 50.0, expiry)
        member.add_coupon(new_coupon)
        return {"status": "success", "coupon": new_coupon}

    def check_available_seats(self, zone_id: str, round_id: str) -> dict:
        zone = self.get_zone(zone_id)
        if zone is None:
            return {"status": "error", "message": "Zone not found"}

        round_obj = zone.get_round(round_id)
        if round_obj is None or not round_obj.is_available(None, None):
            return {"status": "error", "message": "Round not available"}

        available = round_obj.get_total_capacity() - round_obj.get_current_visitor_count()
        if available <= 0:
            return {"status": "error", "message": "No seats available"}
        return {"status": "success", "available_seats": available}