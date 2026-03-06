"""
Payment entity – transaction record for a booking payment
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from utils.id_generator import generate_payment_id

if TYPE_CHECKING:
    from models.booking import Booking


class PaymentMethod:
    """
    Interface for payment methods (cash / QR)
    """

    def pay(self, amount: float) -> bool:
        raise NotImplementedError("pay() must be implemented in subclasses")


class CashPayment(PaymentMethod):
    """
    Cash payment – always succeeds
    """

    def pay(self, amount: float) -> bool:
        print(f"[CASH] Paying {amount} baht")
        return True


class QRPayment(PaymentMethod):
    """
    QR payment – simulate scanning process
    """

    def pay(self, amount: float) -> bool:
        print(f"[QR] Scanning QR for {amount} baht")
        return True     # สามารถเปลี่ยนเป็น random fail ได้ถ้าต้องการ
        

class Payment:
    """
    Represents a payment transaction record
    """

    def __init__(self, amount: float, booking: "Booking", payment_method: PaymentMethod):

        self.__payment_id = generate_payment_id()
        self.__amount = amount
        self.__booking = booking
        self.__method = payment_method
        self.__status = "Pending"      # Pending → Success/Failed

    # Properties
    @property
    def payment_id(self):
        return self.__payment_id

    @property
    def amount(self):
        return self.__amount

    @property
    def booking(self):
        return self.__booking

    @property
    def method(self):
        return self.__method

    @property
    def status(self):
        return self.__status

    # Execute payment
    def pay(self, amount: float) -> bool:
        return self.__method.pay(amount)

    def updateStatus(self, new_status: str):
        self.__status = new_status

    def __repr__(self):
        return (
            f"Payment({self.__payment_id}, amount={self.__amount}, "
            f"status={self.__status})"
        )
