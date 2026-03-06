"Payment service that delegates business flow to BookingService."

from __future__ import annotations

from typing import Optional

from models.booking import Booking
from models.payment import PaymentMethod
from models.park import Park
from services.booking_service import BookingService


class PaymentService:
    """Thin service kept for compatibility with older call sites."""

    def __init__(self, park: Park):
        self._booking_service = BookingService(park)

    def process_payment(
        self,
        booking: Booking,
        phone_number: str,
        payment_method: PaymentMethod,
        coupon_code: Optional[str] = None,
    ):
        return self._booking_service.process_payment(
            booking=booking,
            phone_number=phone_number,
            payment_method=payment_method,
            coupon_code=coupon_code,
        )