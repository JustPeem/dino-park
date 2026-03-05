from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from utils.id_generator import generate_payment_id

if TYPE_CHECKING:
    from .booking import Booking
    from services.payment_service import PaymentMethod


class Payment:
    """
    Payment = Transaction / Receipt
    Created AFTER successful payment.
    """

    def __init__(self,booking: "Booking",payment_method: "PaymentMethod",amount: float,discount: float = 0.0):
        self._payment_id = generate_payment_id()
        self._booking = booking
        self._payment_method = payment_method
        self._amount = amount
        self._discount = discount
        self._payment_date = datetime.now()
        self._status = "COMPLETED"

    @property
    def payment_id(self) -> str:
        return self._payment_id

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def discount(self) -> float:
        return self._discount

    @property
    def status(self) -> str:
        return self._status

    @property
    def payment_method(self) -> str:
        return self._payment_method.get_method_name()

    def refund(self) -> float:
        """
        Refund money from this transaction
        """
        if self._status != "COMPLETED":
            raise ValueError("Cannot refund a non-completed payment")

        refund_amount = round(self._amount * 0.5, 2)
        self._status = "REFUNDED"

        print(f"[Refund] {refund_amount}฿ for Payment {self._payment_id}")
        return refund_amount

    def __repr__(self):
        return f"Payment({self._payment_id}, {self._amount}฿, {self._status})"