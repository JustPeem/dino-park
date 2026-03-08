#   Booking : B-YYYYMMDD-XXX  e.g. B-20250601-001
#   Ticket  : T-XXX           e.g. T-042
#   Trip    : TR-XXX          e.g. TR-007
#   Member  : M-XXX           e.g. M-015
#   Staff   : S-XXX           e.g. S-003
#   Zone    : Z-XX            e.g. Z-01
#   Cage    : C-XXX           e.g. C-012
#   Payment : P-XXX           e.g. P-001

from datetime import date


class IDGenerator:
    """
    Centralized, stateful ID generator for all entities.
    Each entity type maintains its own independent counter.
    """

    def __init__(self):
        self.__counters: dict[str, int] = {
            "booking": 0,
            "ticket": 0,
            "trip": 0,
            "member": 0,
            "staff": 0,
            "zone": 0,
            "cage": 0,
            "payment": 0,
        }

    def __next(self, entity: str) -> int:
        if entity not in self.__counters:
            raise ValueError(f"Unknown entity type: '{entity}'.")
        self.__counters[entity] += 1
        return self.__counters[entity]

    def __validate_entity(self, entity: str) -> None:
        if not isinstance(entity, str) or not entity.strip():
            raise TypeError("entity must be a non-empty string.")
        if entity not in self.__counters:
            raise ValueError(f"Unknown entity type: '{entity}'.")

    def reset(self, entity: str | None = None) -> None:
        """Reset one counter or all counters back to 0."""
        if entity is None:
            for key in self.__counters:
                self.__counters[key] = 0
            return

        self.__validate_entity(entity)
        self.__counters[entity] = 0

    def booking_id(self, booking_date: date | None = None) -> str:
        """Generate Booking ID: B-YYYYMMDD-XXX."""
        d = booking_date or date.today()
        n = self.__next("booking")
        return f"B-{d.strftime('%Y%m%d')}-{n:03d}"

    def ticket_id(self) -> str:
        """Generate Ticket ID: T-XXX."""
        n = self.__next("ticket")
        return f"T-{n:03d}"

    def trip_id(self) -> str:
        """Generate Trip ID: TR-XXX."""
        n = self.__next("trip")
        return f"TR-{n:03d}"

    def member_id(self) -> str:
        """Generate Member ID: M-XXX."""
        n = self.__next("member")
        return f"M-{n:03d}"

    def staff_id(self) -> str:
        """Generate Staff ID: S-XXX."""
        n = self.__next("staff")
        return f"S-{n:03d}"

    def zone_id(self) -> str:
        """Generate Zone ID: Z-XX."""
        n = self.__next("zone")
        return f"Z-{n:02d}"

    def cage_id(self) -> str:
        """Generate Cage ID: C-XXX."""
        n = self.__next("cage")
        return f"C-{n:03d}"

    def payment_id(self) -> str:
        """Generate Payment ID: P-XXX."""
        n = self.__next("payment")
        return f"P-{n:03d}"


id_gen = IDGenerator()