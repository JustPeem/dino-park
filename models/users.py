from abc import ABC
from typing import TYPE_CHECKING
import re

if TYPE_CHECKING:
    from coupon import Coupon

MEMBER_DISCOUNT_RATE = 0.10
GROUP_DISCOUNT_RATE = 0.05
GROUP_DISCOUNT_MIN_SEATS = 10


class User(ABC):
    """Abstract base class for all users in the system."""

    def __init__(self, name: str, phone_number: str, user_type: str):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")
        if not isinstance(phone_number, str) or not re.fullmatch(r"\d{10}", phone_number):
            raise ValueError("phone_number must be a 10-digit string.")

        self.__name = name.strip()
        self.__phone_number = phone_number
        self.__user_type = user_type

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def user_type(self) -> str:
        return self.__user_type

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.__name}, phone={self.__phone_number})"


class Member(User):
    """Registered member with coupons and discount capabilities."""

    def __init__(self, name: str, phone_number: str):
        super().__init__(name, phone_number, user_type="member")
        self.__coupons: list["Coupon"] = []

    @property
    def coupons(self) -> list["Coupon"]:
        return self.__coupons

    def add_coupon(self, coupon: "Coupon") -> None:
        """Add a coupon to the member's coupon list."""
        from coupon import Coupon
        if not isinstance(coupon, Coupon):
            raise TypeError("coupon must be a Coupon instance.")
        self.__coupons.append(coupon)

    def use_coupon(self, coupon_code: str, base_price: float) -> bool:
        """
        Attempt to use a coupon by code.
        Returns True if coupon was successfully applied, False otherwise.
        """
        if not isinstance(coupon_code, str) or not coupon_code.strip():
            raise ValueError("coupon_code must be a non-empty string.")
        if not isinstance(base_price, (int, float)) or base_price < 0:
            raise ValueError("base_price must be a non-negative number.")

        for coupon in self.__coupons:
            if coupon.coupon_code == coupon_code:
                if coupon.is_valid():
                    discounted_price = base_price - coupon.discount_amount
                    coupon.mark_used()
                    print(f"Coupon '{coupon_code}' applied. Price: {base_price} -> {discounted_price:.2f}")
                    return True
                else:
                    print(f"Coupon '{coupon_code}' is invalid or already used.")
                    return False
        print(f"Coupon '{coupon_code}' not found.")
        return False

    def calculate_discount(self, base_price: float, seats: int = 1, coupon_code: str = None) -> float:
        """
        Calculate the final price after applying all applicable discounts:
          1. Member discount: 10%
          2. Group discount: 5% if seats >= 10
          3. Coupon discount: fixed amount from a valid coupon

        Returns the final discounted price (minimum 0.0).
        """
        if not isinstance(base_price, (int, float)) or base_price < 0:
            raise ValueError("base_price must be a non-negative number.")
        if not isinstance(seats, int) or seats < 1:
            raise ValueError("seats must be a positive integer.")
        if coupon_code is not None and (not isinstance(coupon_code, str) or not coupon_code.strip()):
            raise ValueError("coupon_code must be a non-empty string or None.")

        price = base_price

        # 1. Member discount (10%)
        price = price * (1 - MEMBER_DISCOUNT_RATE)

        # 2. Group discount (5% if >= 10 seats)
        if seats >= GROUP_DISCOUNT_MIN_SEATS:
            price = price * (1 - GROUP_DISCOUNT_RATE)

        # 3. Coupon discount (fixed amount)
        if coupon_code:
            for coupon in self.__coupons:
                if coupon.coupon_code == coupon_code and coupon.is_valid():
                    price = price - coupon.discount_amount
                    break

        return max(0.0, price)

    def get_valid_coupons(self) -> list["Coupon"]:
        """Return a list of all valid (unused and non-expired) coupons."""
        return [c for c in self.__coupons if c.is_valid()]

    def __repr__(self):
        return f"Member(name={self.name}, phone={self.phone_number}, coupons={len(self.__coupons)})"


class GuestUser(User):
    """Guest user without membership privileges."""

    def __init__(self, name: str, phone_number: str):
        super().__init__(name, phone_number, user_type="guest")

    def __repr__(self):
        return f"GuestUser(name={self.name}, phone={self.phone_number})"