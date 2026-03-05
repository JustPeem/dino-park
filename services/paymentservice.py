"""
PaymentService – calculates total, validates coupon, and processes payment
"""

from __future__ import annotations
from typing import Optional
from models.booking import Booking
from models.member import Member
from models.payment import PaymentMethod


class PaymentService:
    """
    Handles full payment logic:
    - Member discount (%)
    - Group discount
    - Feeding ticket add-ons
    - Coupon deduction
    - Execute transaction
    """

    def __init__(self, park):
        self.park = park

    def process_payment(
        self,
        booking: Booking,
        phone_number: str,
        payment_method: PaymentMethod,
        coupon_code: Optional[str] = None
    ):
        """
        Final price logic:
        total = seats * base_price + feeding_tickets*150
              - member_discount
              - group_discount
              - coupon_value
        """

        # 1) Find member by phone number
        member: Optional[Member] = self.park.findMemberByPhoneNumber(phone_number)

        member_discount_percent = 0
        coupon_discount = 0

        # 2) If member exists → apply discount
        if member:

            # Member percentage discount
            member_discount_percent = member.calculateDiscount(booking.base_price)

            # If coupon provided
            if coupon_code:
                coupon_discount = member.UseCoupon(coupon_code, booking.base_price)

        # 3) Calculate final price (in booking)
        final_price = booking.calculate_final_price(
            member_discount_percent=member_discount_percent,
            coupon_discount=coupon_discount
        )

        # 4) Create payment transaction
        payment = booking.create_payment(payment_method)

        # 5) Execute the transaction
        result = payment.pay(final_price)

        if result:
            payment.updateStatus("Success")
            return booking.confirm_booking()   # generate tickets
        else:
            payment.updateStatus("Failed")
            raise Exception("Payment failed")
