from datetime import datetime, timedelta

COUPON_VALIDITY_DAYS = 30


class Coupon:
    def __init__(self, coupon_code: str, discount_amount: float, expiry_date: datetime):
        self.__coupon_code = coupon_code.strip()
        self.__discount_amount = float(discount_amount)
        self.__expiry_date = expiry_date
        self.__is_used = False

    @classmethod
    def create(cls, coupon_code: str, discount_amount: float, expiry_date: datetime | None = None) -> "Coupon":
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=COUPON_VALIDITY_DAYS)
        return cls(coupon_code, discount_amount, expiry_date)

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
        return not self.__is_used and datetime.now() <= self.__expiry_date

    def mark_used(self) -> None:
        self.__is_used = True

    def __repr__(self):
        return f"Coupon(code={self.__coupon_code}, discount={self.__discount_amount}, used={self.__is_used})"