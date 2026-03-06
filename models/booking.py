"""
Booking entity – represents a visitor booking
"""

from __future__ import annotations
from typing import TYPE_CHECKING, List

from utils.id_generator import generate_booking_id

if TYPE_CHECKING:
    from .users import User
    from .round import Round
    from .trip import Trip
    from .payment import Payment, PaymentMethod
    from .ticket import Ticket


class Booking:
    """
    Represents a booking made by a user for a specific round and trip.
    Handles: seat reservation, pricing, payment transaction, ticket creation.
    """

    def __init__(
        self,
        user: "User",
        round_ref: "Round",
        trip: "Trip",
        seats: int,
        base_price: float
    ):

        self.__booking_id = generate_booking_id()

        # relationships
        self.__user = user
        self.__round = round_ref
        self.__trip = trip

        # booking details
        self.__seats = seats
        self.__base_price = base_price
        self.__total_price = base_price * seats
        self.__status = "PENDING"    # PENDING → PAID → CANCELLED

        # tickets & payment records
        self.__tickets: List["Ticket"] = []
        self.__payments: List["Payment"] = []

        #feeding ticket
        self.__feeding_tickets = 0
        self.__feeding_ticket_price = 150


    # ─────────────────────────────
    # Properties
    # ─────────────────────────────
    @property
    def booking_id(self):
        return self.__booking_id

    @property
    def user(self):
        return self.__user

    @property
    def round(self):
        return self.__round

    @property
    def trip(self):
        return self.__trip

    @property
    def seats(self):
        return self.__seats

    @property
    def base_price(self):
        return self.__base_price

    @property
    def total_price(self):
        return self.__total_price

    @property
    def status(self):
        return self.__status

    @property
    def tickets(self):
        return self.__tickets

    # ─────────────────────────────
    # Price Calculation
    # ─────────────────────────────

    def calculate_final_price(self,member_discount_percent: float,coupon_discount: float = 0) -> float:
        """
    Calculate final price including:
    - member % discount
    - group discount (5% if seats >= 10)
    - feeding ticket add-ons
    - coupon (fixed amount)
        """

        # base seats + feeding tickets
        normal_price = self.__base_price * self.__seats
        feeding_price = self.__feeding_ticket_price * self.__feeding_tickets

        total_before_discount = normal_price + feeding_price

        # member discount in %
        member_discount_value = (member_discount_percent / 100) * total_before_discount

        # group discount (≥10 seats)
        group_discount_value = 0
        if self.__seats >= 10:
            group_discount_value = 0.05 * total_before_discount

        # total discount
        total_discount = member_discount_value + group_discount_value + coupon_discount

        # final price cannot go below 0
        final_price = max(0, total_before_discount - total_discount)

        # update booking
        self.__total_price = final_price

        return final_price


    # ─────────────────────────────
    # Payment Transaction (Not Pricing)
    # ─────────────────────────────

    def create_payment(self, method: "PaymentMethod") -> "Payment":
        """
        Creates a payment record (transaction), not pricing logic.
        """
        from .payment import Payment

        payment = Payment(
            amount=self.__total_price,
            booking=self,
            payment_method=method
        )

        self.__payments.append(payment)
        return payment

    # ─────────────────────────────
    # Confirm Booking
    # ─────────────────────────────

    def confirm_booking(self):
        """
        Called when payment is successful.
        Generates tickets and marks booking as PAID.
        """
        if self.__status == "PAID":
            raise Exception("Booking already paid.")

        if self.__status == "CANCELLED":
            raise Exception("Cannot confirm: booking was cancelled.")

        self.__status = "PAID"

        # generate tickets based on seats
        from .ticket import Ticket
        for i in range(self.__seats):
            ticket = Ticket(
                round_ref=self.__round,
                trip=self.__trip,
                price=self.__base_price,
                seat_number=i + 1
            )
            self.__tickets.append(ticket)

        return self.__tickets

    # ─────────────────────────────
    # Cancel Booking
    # ─────────────────────────────

    def cancel(self):
        """
        Cancel booking, release seats, refund done elsewhere (BookingService).
        """
        if self.__status == "CANCELLED":
            raise Exception("Booking already cancelled.")

        if self.__status == "PAID":
            raise Exception("Cannot cancel: booking already paid. Use refund().")

        self.__status = "CANCELLED"

        # release reserved seats
        self.__trip.cancel_reservation(self.__seats)

    # ─────────────────────────────
    # Refund
    # ─────────────────────────────

    def refund(self):
        """
        Refund booking (after payment). PaymentService handles the logic.
        Only update booking & trip state.
        """
        if self.__status != "PAID":
            raise Exception("Refund failed: booking not paid.")

        self.__status = "REFUNDED"

        # refund seats
        self.__trip.cancel_reservation(self.__seats)

    # ─────────────────────────────
    # Ticket Access
    # ─────────────────────────────

    def get_ticket(self, ticket_id: str) -> "Ticket":
        for t in self.__tickets:
            if t.ticket_id == ticket_id:
                return t
        return None

    # ─────────────────────────────
    # Debug
    # ─────────────────────────────

    def __repr__(self):
        return (
            f"Booking({self.__booking_id}, seats={self.__seats}, "
            f"total={self.__total_price}, status={self.__status})"
        )
