from __future__ import annotations

from typing import TYPE_CHECKING

from utils.id_generator import id_gen

if TYPE_CHECKING:
    from .booking import Booking


class PaymentMethod:
    def pay(self, amount: float) -> bool:
        raise NotImplementedError


class CashPayment(PaymentMethod):
    def pay(self, amount: float) -> bool:
        return amount >= 0


class QRPayment(PaymentMethod):
    def pay(self, amount: float) -> bool:
        return amount >= 0


class Payment:
    def __init__(self, amount: float, booking: "Booking", payment_method: PaymentMethod):
        self.__payment_id = f"P-{id_gen.trip_id()}"
        self.__amount = amount
        self.__booking = booking
        self.__method = payment_method
        self.__status = "PENDING"

    @property
    def status(self):
        return self.__status

    def pay(self) -> bool:
        ok = self.__method.pay(self.__amount)
        self.__status = "SUCCESS" if ok else "FAILED"
        return ok
