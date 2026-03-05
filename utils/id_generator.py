# id_generator.py
# Centralized ID generation for all entities in the system.
#
# Format per spec:
#   Booking : B-YYYYMMDD-XXX   e.g. B-20250601-001
#   Ticket  : T-XXX            e.g. T-042
#   Trip    : TR-XXX           e.g. TR-007
#   Member  : M-XXX            e.g. M-015
#   Staff   : S-XXX            e.g. S-003
#   Zone    : Z-XX             e.g. Z-01
#   Cage    : C-XXX            e.g. C-012

from datetime import date


class IDGenerator:
    """
    Centralized, stateful ID generator for all entities.
    Each entity type maintains its own independent counter.
    Counters start at 1 and increment with every call.
    """

    def __init__(self):
        self.__counters: dict[str, int] = {
            "booking": 0,
            "ticket":  0,
            "trip":    0,
            "member":  0,
            "staff":   0,
            "zone":    0,
            "cage":    0,
        }

    # ── private helper ──────────────────────────────────────────
    def __next(self, entity: str) -> int:
        """Increment and return the next counter value for an entity."""
        if entity not in self.__counters:
            raise ValueError(f"Unknown entity type: '{entity}'.")
        self.__counters[entity] += 1
        return self.__counters[entity]

    def __validate_entity(self, entity: str) -> None:
        """Validate that entity is a non-empty string and known type."""
        if not isinstance(entity, str) or not entity.strip():
            raise TypeError("entity must be a non-empty string.")
        if entity not in self.__counters:
            raise ValueError(f"Unknown entity type: '{entity}'.")

    def reset(self, entity: str = None) -> None:
        """
        Reset counter(s) back to 0.
        If entity is None, resets ALL counters (useful for testing).
        """
        if entity is None:
            for key in self.__counters:
                self.__counters[key] = 0
        else:
            self.__validate_entity(entity)
            self.__counters[entity] = 0

    def current(self, entity: str) -> int:
        """Return the current counter value without incrementing."""
        self.__validate_entity(entity)
        return self.__counters[entity]

    # ── public generators ────────────────────────────────────────
    def booking_id(self, booking_date: date = None) -> str:
        """
        Generate a Booking ID.
        Format: B-YYYYMMDD-XXX
        e.g.  : B-20250601-001

        booking_date must be today or within the next 30 days (per spec).
        """
        if booking_date is None:
            booking_date = date.today()
        if not isinstance(booking_date, date):
            raise TypeError("booking_date must be a date instance.")
        today = date.today()
        if booking_date < today:
            raise ValueError("booking_date must not be in the past.")
        if (booking_date - today).days > 30:
            raise ValueError("booking_date must be within 30 days from today (per spec).")
        n = self.__next("booking")
        return f"B-{booking_date.strftime('%Y%m%d')}-{n:03d}"

    def ticket_id(self) -> str:
        """
        Generate a Ticket ID.
        Format: T-XXX
        e.g.  : T-042
        """
        n = self.__next("ticket")
        return f"T-{n:03d}"

    def trip_id(self) -> str:
        """
        Generate a Trip ID.
        Format: TR-XXX
        e.g.  : TR-007
        """
        n = self.__next("trip")
        return f"TR-{n:03d}"

    def member_id(self) -> str:
        """
        Generate a Member ID.
        Format: M-XXX
        e.g.  : M-015
        """
        n = self.__next("member")
        return f"M-{n:03d}"

    def staff_id(self) -> str:
        """
        Generate a Staff ID.
        Format: S-XXX
        e.g.  : S-003
        """
        n = self.__next("staff")
        return f"S-{n:03d}"

    def zone_id(self) -> str:
        """
        Generate a Zone ID.
        Format: Z-XX
        e.g.  : Z-01
        """
        n = self.__next("zone")
        return f"Z-{n:02d}"

    def cage_id(self) -> str:
        """
        Generate a Cage ID.
        Format: C-XXX
        e.g.  : C-012
        """
        n = self.__next("cage")
        return f"C-{n:03d}"


# ── Singleton instance ───────────────────────────────────────────
# Import and use this single instance across the entire system:
#   from utils.id_generator import id_gen
#   booking_id = id_gen.booking_id()
id_gen = IDGenerator()