from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from cage import Cage
    from round import Round
    from ranger import Ranger

class Zone:
    def __init__(self, zone_id: str, zone_type: str):
        """
        zone_id follows format Z-XX  e.g. "Z-01", "Z-12"
        """
        self.__zone_id = zone_id
        self.__zone_type = zone_type
        self.__rangers: list["Ranger"] = []
        self.__rounds: list["Round"] = []
        self.__cages: list["Cage"] = []

    # ── Properties ────────────────────────────────
    @property
    def zone_id(self) -> str:
        return self.__zone_id
    
    @property
    def zone_type(self) -> str:
        return self.__zone_type
    
    # ── Cage management  (Ranger food-refill flow) ────────────────────────
    def add_cage(self, cage: "Cage") -> None:
        self.__cages.append(cage)

    # kept for backward-compat with Park sequence calls
    def get_cages(self) -> list["Cage"]:
        return self.__cages

    # ── Round management ──────────────────────────────────────────────────
    def add_round(self, round_obj: "Round") -> None:
        self.__rounds.append(round_obj)

    def get_round(self, round_id: str) -> Optional["Round"]:
        """Return Round by id, or None (used in booking & seat-check flows)."""
        for r in self.__rounds:
            if r.round_id == round_id:
                return r
        return None

    def check_round(self, start: datetime, end: datetime) -> Optional["Round"]:
        """
        Return the first available Round for the given time window.
        Used by Park.create_trip (Manager sequence diagram).
        """
        for r in self.__rounds:
            if r.is_available(start, end):
                return r
        return None

    # ── Availability  (Member check-available-seats flow) ─────────────────
    def check_availability(self, start: Optional[datetime],
                           end: Optional[datetime]) -> bool:
        """Returns True if zone is open/operational."""
        return True  # default: zone is available

    # ── Ranger management ─────────────────────────────────────────────────
    def add_ranger(self, ranger: "Ranger") -> None:
        self.__rangers.append(ranger)

    def __repr__(self) -> str:
        return f"Zone(id={self.__zone_id!r}, type={self.__zone_type!r})"