from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from utils.id_generator import id_gen

if TYPE_CHECKING:
    from .coupon import Coupon

MEMBER_DISCOUNT_PERCENT = 10.0


class User(ABC):
    def __init__(self, name: str, phone_number: str, user_type: str, user_id: str):
        self.__name = name
        self.__phone_number = phone_number
        self.__user_type = user_type
        self.__user_id = user_id

    @property
    def user_id(self) -> str:
        return self.__user_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def user_type(self) -> str:
        return self.__user_type

    @abstractmethod
    def __repr__(self):
        ...


class Member(User):
    def __init__(self, name: str, phone_number: str):
        super().__init__(name, phone_number, user_type="member", user_id=id_gen.member_id())
        self.__coupons: list["Coupon"] = []

    def add_coupon(self, coupon: "Coupon") -> None:
        self.__coupons.append(coupon)

    def use_coupon(self, coupon_code: str) -> float:
        for coupon in self.__coupons:
            if coupon.coupon_code == coupon_code and coupon.is_valid():
                coupon.mark_used()
                return coupon.discount_amount
        return 0.0

    def member_discount_percent(self) -> float:
        return MEMBER_DISCOUNT_PERCENT

    def get_active_food_coupon(self) -> "Coupon | None":
        for coupon in self.__coupons:
            if coupon.coupon_code == "FOOD_COUPON" and coupon.is_valid():
                return coupon
        return None

    def __repr__(self):
        return f"Member(id={self.user_id}, name={self.name})"


class GuestUser(User):
    def __init__(self, name: str, phone_number: str):
        super().__init__(name, phone_number, user_type="guest", user_id=f"G-{phone_number}")

    def __repr__(self):
        return f"GuestUser(id={self.user_id}, name={self.name})"