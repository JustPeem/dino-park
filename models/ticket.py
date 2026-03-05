# Ticket

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from round import Round

TICKET_PRICES: dict[str, float] = {
    "adult":   500.0,
    "child":   300.0,   # age <= 12
    "senior":  250.0,   # age >= 60
    "feeding": 150.0,   # add-on feeding ticket
}

TICKET_ID_PATTERN = re.compile(r"^T-\d{3}$")  # T-XXX e.g. T-042


class Ticket:
    """
    Represents a ticket for a visitor to attend a round/trip.

    ticket_type: "adult" | "child" | "senior" | "feeding"
    ticket_id format: T-XXX  e.g. T-042
    """

    def __init__(
        self,
        ticket_id: str,
        round: "Round",
        seat_number: int,
        ticket_type: str = "adult",
    ):
        if not isinstance(ticket_id, str) or not TICKET_ID_PATTERN.match(ticket_id):
            raise ValueError(f"ticket_id must match format 'T-XXX'. Got '{ticket_id}'.")
        if ticket_type not in TICKET_PRICES:
            raise ValueError(f"Invalid ticket_type '{ticket_type}'. Must be one of {list(TICKET_PRICES)}.")
        if not isinstance(seat_number, int) or seat_number < 1:
            raise ValueError("seat_number must be a positive integer.")
        if round is None:
            raise ValueError("round must not be None.")

        self.__ticket_id = ticket_id
        self.__price = TICKET_PRICES[ticket_type]
        self.__round = round
        self.__seat_number = seat_number
        self.__is_used = False
        self.__type = ticket_type

    @classmethod
    def create(cls, ticket_id: str, round: "Round", seat_number: int, ticket_type: str = "adult") -> "Ticket":
        """
        Factory method to create a new Ticket.
        Used in sequence: Ticket.create() → ticket object
        """
        ticket = cls(ticket_id, round, seat_number, ticket_type)
        print(f"[Ticket] Created: id={ticket_id}, type={ticket_type}, seat={seat_number}, price={ticket.price}")
        return ticket

    @property
    def ticket_id(self) -> str:
        return self.__ticket_id

    @property
    def price(self) -> float:
        return self.__price

    @property
    def round(self) -> "Round":
        return self.__round

    @property
    def seat_number(self) -> int:
        return self.__seat_number

    @property
    def is_used(self) -> bool:
        return self.__is_used

    @property
    def type(self) -> str:
        return self.__type

    def check_is_used(self) -> bool:
        """
        Return whether this ticket has been used.
        Used in sequence: Ticket.isUsed() → bool isUsed
        """
        return self.__is_used

    def set_used(self, value: bool) -> None:
        """Mark this ticket as used or unused."""
        if not isinstance(value, bool):
            raise TypeError("value must be a boolean.")
        self.__is_used = value
        status = "used" if value else "unused"
        print(f"[Ticket {self.__ticket_id}] Marked as {status}.")

    @staticmethod
    def get_price(ticket_type: str) -> float:
        """Return the base price for a given ticket type."""
        if ticket_type not in TICKET_PRICES:
            raise ValueError(f"Invalid ticket_type '{ticket_type}'. Must be one of {list(TICKET_PRICES)}.")
        return TICKET_PRICES[ticket_type]

    def __repr__(self):
        return (
            f"Ticket(id={self.__ticket_id}, seat={self.__seat_number}, "
            f"type={self.__type}, price={self.__price}, used={self.__is_used})"
        )