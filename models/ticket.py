from __future__ import annotations

from typing import TYPE_CHECKING

from utils.id_generator import id_gen

if TYPE_CHECKING:
    from .round import Round


TICKET_PRICES: dict[str, float] = {
    "adult": 500.0,
    "child": 300.0,
    "senior": 250.0,
    "feeding": 150.0,
}


class Ticket:
    def __init__(self, round_ref: "Round", seat_number: int, ticket_type: str = "adult"):
        self.__ticket_id = id_gen.ticket_id()
        self.__round = round_ref
        self.__seat_number = seat_number
        self.__type = ticket_type
        self.__price = TICKET_PRICES[ticket_type]
        self.__is_used = False

    @property
    def ticket_id(self) -> str:
        return self.__ticket_id

    @property
    def is_used(self) -> bool:
        return self.__is_used

    def set_used(self, value: bool) -> None:
        self.__is_used = value

    @property
    def price(self) -> float:
        return self.__price