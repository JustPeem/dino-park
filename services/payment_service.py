from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING

from utils.id_generator import generate_payment_id

if TYPE_CHECKING:
    from models.booking import Booking


# ─────────────────────────────
# Payment Transaction
# ─────────────────────────────

class Payment:

    def __init__(self, amount: float, method: str):

        self.__payment_id = generate_payment_id()
        self.__amount = amount
        self.__method = method
        self.__timestamp = datetime.now()
        self.__status = "SUCCESS"

    def get_payment_id(self):
        return self.__payment_id

    def get_amount(self):
        return self.__amount

    def get_method(self):
        return self.__method

    def get_timestamp(self):
        return self.__timestamp

    def get_status(self):
        return self.__status


# ─────────────────────────────
# Payment Method Interface
# ─────────────────────────────

class PaymentMethod(ABC):

    @abstractmethod
    def pay(self, amount: float) -> Payment:
        pass

    @abstractmethod
    def get_method_name(self) -> str:
        pass


# ─────────────────────────────
# Cash Payment
# ─────────────────────────────

class CashPayment(PaymentMethod):

    def __init__(self, amount_tendered: float):
        self.__amount_tendered = amount_tendered

    def pay(self, amount: float) -> Payment:

        if self.__amount_tendered < amount:
            raise ValueError("Not enough cash")

        change = self.__amount_tendered - amount

        print(f"[Cash] Paid {amount}฿ Change {change}฿")

        return Payment(amount, self.get_method_name())

    def get_method_name(self) -> str:
        return "CASH"


# ─────────────────────────────
# QR Payment
# ─────────────────────────────

class QRPayment(PaymentMethod):

    def __init__(self, account_ref: str):
        self.__account_ref = account_ref
        self.__qr_code = None

    def __generate_qr(self, amount: float):

        self.__qr_code = f"QR|{self.__account_ref}|{amount}"

        print("QR generated:", self.__qr_code)

        return self.__qr_code

    def pay(self, amount: float) -> Payment:

        qr = self.__generate_qr(amount)

        print(f"[QR] Payment {amount} success via {qr}")

        return Payment(amount, self.get_method_name())

    def get_method_name(self) -> str:
        return "QR"