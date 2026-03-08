from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .cage import Cage
    from .round import Round


class Zone:
    def __init__(self, zone_id: str, zone_type: str):
        self.__zone_id = zone_id
        self.__zone_type = zone_type
        self.__rounds: list["Round"] = []
        self.__cages: list["Cage"] = []

    @property
    def zone_id(self) -> str:
        return self.__zone_id

    @property
    def zone_type(self) -> str:
        return self.__zone_type

    @property
    def rounds(self) -> list["Round"]:
        return self.__rounds

    def add_cage(self, cage: "Cage") -> None:
        self.__cages.append(cage)

    def get_cages(self) -> list["Cage"]:
        return self.__cages

    def add_round(self, round_obj: "Round") -> None:
        self.__rounds.append(round_obj)

    def get_round(self, round_id: str) -> Optional["Round"]:
        for round_obj in self.__rounds:
            if round_obj.round_id == round_id:
                return round_obj
        return None

    def check_round(self, start: datetime, end: datetime) -> Optional["Round"]:
        for round_obj in self.__rounds:
            if round_obj.is_available(start, end):
                return round_obj
        return None

    def check_availability(self, start: datetime | None, end: datetime | None) -> bool:
        return True