# Coupon

from datetime import datetime, timedelta

COUPON_VALIDITY_DAYS = 30


class Coupon:
    """Represents a discount coupon that can be owned and used by a Member."""

    def __init__(
        self,
        coupon_code: str,
        discount_amount: float,
        expiry_date: datetime,
    ):
        if not isinstance(coupon_code, str) or not coupon_code.strip():
            raise ValueError("coupon_code must be a non-empty string.")
        if not isinstance(discount_amount, (int, float)) or discount_amount <= 0:
            raise ValueError("discount_amount must be a positive number.")
        if not isinstance(expiry_date, datetime):
            raise TypeError("expiry_date must be a datetime instance.")
        if expiry_date <= datetime.now():
            raise ValueError("expiry_date must be in the future.")

        self.__coupon_code = coupon_code.strip()
        self.__discount_amount = float(discount_amount)
        self.__expiry_date = expiry_date
        self.__is_used = False

    @classmethod
    def create(cls, coupon_code: str, discount_amount: float, expiry_date: datetime = None) -> "Coupon":
        """
        Factory method to create a new Coupon.
        If expiry_date is not given, defaults to 30 days from now.
        Used in sequence: Coupon.create(foodType, expiryDate)
        """
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=COUPON_VALIDITY_DAYS)
        coupon = cls(coupon_code, discount_amount, expiry_date)
        print(f"[Coupon] Created: code={coupon_code}, discount={discount_amount}, expiry={expiry_date.date()}")
        return coupon

    @property
    def coupon_code(self) -> str:
        return self.__coupon_code

    @property
    def discount_amount(self) -> float:
        return self.__discount_amount

    @property
    def expiry_date(self) -> datetime:
        return self.__expiry_date

    @property
    def is_used(self) -> bool:
        return self.__is_used

    def is_valid(self) -> bool:
        """Return True if the coupon is unused and not expired."""
        return not self.__is_used and datetime.now() <= self.__expiry_date

    def mark_used(self) -> None:
        """Mark this coupon as used."""
        self.__is_used = True
        print(f"[Coupon {self.__coupon_code}] Marked as used.")

    def __repr__(self):
        return (
            f"Coupon(code={self.__coupon_code}, discount={self.__discount_amount}, "
            f"expiry={self.__expiry_date.date()}, used={self.__is_used})"
        )