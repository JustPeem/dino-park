from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from utils.id_generator import id_gen

if TYPE_CHECKING:
    from .users import User
    from .round import Round
    from .trip import Trip
    from .payment import PaymentMethod


class Booking:
    def __init__(self, user: "User", round_ref: "Round", trip: "Trip", seats: int, base_price: float):
        self.__booking_id = id_gen.booking_id(round_ref.date)
        self.__booking_date = datetime.now()
        self.__user = user
        self.__round = round_ref
        self.__trip = trip
        self.__seats = seats
        self.__base_price = base_price
        self.__total_price = base_price * seats
        self.__status = "PENDING"
        self.__tickets = []
        self.__payments = []

    @property
    def booking_id(self):
        return self.__booking_id

    @property
    def booking_date(self):
        return self.__booking_date

    @property
    def trip(self):
        return self.__trip

    @property
    def status(self):
        return self.__status

    @property
    def tickets(self):
        return self.__tickets

    @property
    def base_price(self):
        return self.__base_price

    @property
    def total_price(self):
        return self.__total_price

    @property
    def seats(self):
        return self.__seats

    def calculate_final_price(self, member_discount_percent: float = 0.0, coupon_discount: float = 0.0) -> float:
        subtotal = self.__base_price * self.__seats
        member_discount = subtotal * (member_discount_percent / 100)
        group_discount = subtotal * 0.05 if self.__seats >= 10 else 0.0
        self.__total_price = max(0.0, subtotal - member_discount - group_discount - coupon_discount)
        return self.__total_price

    def create_payment(self, method: "PaymentMethod"):
        from .payment import Payment

        payment = Payment(amount=self.__total_price, booking=self, payment_method=method)
        self.__payments.append(payment)
        return payment

    def confirm_booking(self):
        from .ticket import Ticket

        if self.__status != "PENDING":
            return self.__tickets
        self.__status = "CONFIRMED"
        if not self.__tickets:
            for seat_number in range(1, self.__seats + 1):
                self.__tickets.append(Ticket(round_ref=self.__round, seat_number=seat_number))
        return self.__tickets

    def cancel_booking(self, booking_id: str) -> bool:
        if booking_id != self.__booking_id:
            return False
        
        if self.__status == "CANCELLED":
            return False
        self.__status = "CANCELLED"
        self.__trip.cancel_reservation(self.__seats)
        return True

    def is_confirmed(self) -> bool:
        return self.__status == "CONFIRMED"

    def get_ticket(self, ticket_id: str):
        for ticket in self.__tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        return None
