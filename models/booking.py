"""
models/booking.py
Booking entity – core transaction object.

States:
PENDING → CONFIRMED → CANCELLED
"""

from __future__ import annotations
from datetime import datetime
from typing import List, TYPE_CHECKING


from utils.id_generator import generate_booking_id
from utils.exceptions import BookingAlreadyCancelledException

if TYPE_CHECKING:
    from .users import User
    from .round import Round
    from .ticket import Ticket
    from .payment import Payment, PaymentMethod
    from .trip import Trip


FEEDING_ADDON = 150.0


class Booking:
    """
    Represents a visitor's park reservation.
    Owns Tickets (Composition) and references User and Round.
    """

    def __init__(self, user: "User", round: "Round", trip: "Trip", seats: int,with_feeding: bool = False):
        self.__booking_id = generate_booking_id()
        self.__booking_date = datetime.now()
        self.__user = user
        self.__round = round
        self.__seats = seats
        self.__trip = trip
        self.__total_price = 0
        self.__tickets: List["Ticket"] = []
        self.__status = "PENDING"
        self.__payment: "Payment | None" = None
        self.__with_feeding = with_feeding

    # ───── Properties ─────

    @property
    def booking_id(self) -> str:
        return self.__booking_id

    @property
    def status(self) -> str:
        return self.__status

    @property
    def total_price(self) -> float:
        return self.__total_price

    @property
    def round(self) -> "Round":
        return self.__round

    @property
    def tickets(self) -> List["Ticket"]:
        return list(self.__tickets)

    # ───── Ticket Generation ─────

    def create_tickets(self, price_per_seat: float) -> List["Ticket"]:
        from .ticket import Ticket

        for seat in range(1, self.__seats + 1):

            if self.__with_feeding:
                ticket_type = Ticket.FEEDING
                price = price_per_seat + FEEDING_ADDON
            else:
                ticket_type = Ticket.STANDARD
                price = price_per_seat

            ticket = Ticket(
                price=price,
                round_=self.__round,
                seat_number=seat,
                ticket_type=ticket_type,
            )

            self.__tickets.append(ticket)

        return self.__tickets
        
    # ───── calcualte_final_price ─────
    def calculate_final_price(self, discount: float) -> float:

        base_price = self.__round.price_per_seat * self.__seats

        

        if self.__with_feeding:
            base_price += FEEDING_ADDON * self.__seats

        final_price = base_price - (base_price * discount / 100)

        if final_price < 0:
            final_price = 0

        self.__total_price = final_price
        return self.__total_price

    # ───── Payment / Transaction ─────

    def create_payment(self, method: "PaymentMethod") -> "Payment":
        """
        Create a payment (transaction) for this booking.
        """
        from .payment import Payment

        payment = Payment(
            booking=self,
            amount=self.__total_price,
            method=method
        )

        self.__payment = payment
        return payment

    # ───── Lifecycle ─────

    def confirm_booking(self) -> None:
        """
        Confirm booking after successful payment.
        """
        if self.__status != "PENDING":
            raise ValueError(f"Cannot confirm booking in state {self.__status}")

        self.__status = "CONFIRMED"

    def cancel_booking(self) -> None:
        """
        Cancel booking and cancel all tickets.
        """
        if self.__status == "CANCELLED":
            raise BookingAlreadyCancelledException(
                f"Booking {self.__booking_id} already cancelled"
            )

        for ticket in self.__tickets:
            ticket.cancel()

        self.__status = "CANCELLED"

    

    # ───── Debug ─────

    def __repr__(self) -> str:
        return (
            f"Booking({self.__booking_id}, "
            f"user={self.__user.name}, "
            f"seats={self.__seats}, "
            f"status={self.__status})"
        )