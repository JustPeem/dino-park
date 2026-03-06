from __future__ import annotations
from typing import Optional

from models.booking import Booking
from models.member import Member
from models.payment import PaymentMethod
from models.park import Park


class BookingService:
    """
    Handles booking creation, pricing, payment, cancellation and refunds.
    """

    def __init__(self, park: Park):
        self.park = park

    # ────────────────────────────────────────────────
    # Create Booking  (Sequence Diagram #1)
    # ────────────────────────────────────────────────

    def create_booking(
        self,
        user_id: str,
        zone_id: str,
        round_id: str,
        trip_id: str,
        seats: int
    ) -> Booking:

        # 1) Get zone
        zone = self.park.getZone(zone_id)
        if zone is None:
            raise Exception("Zone not found")

        # 2) Get round
        round_ref = zone.getRound(round_id)
        if round_ref is None:
            raise Exception("Round not found")

        # 3) Get trip
        trip = round_ref.getTrip(trip_id)
        if trip is None:
            raise Exception("Trip not found")

        # 4) Check seat availability
        if not trip.check_seat_availability(seats):
            raise Exception("Not enough seats")

        # 5) Reserve seats
        trip.reserve_seats(seats)

        # 6) Get user
        user = self.park.getUserById(user_id)
        if user is None:
            raise Exception("User not found")

        # 7) Use base price of round (price per seat)
        base_price = round_ref.price_per_seat

        # 8) Create booking
        booking = Booking(
            user=user,
            round_ref=round_ref,
            trip=trip,
            seats=seats,
            base_price=base_price
        )

        return booking

    # ────────────────────────────────────────────────
    # Payment Flow  (Sequence Diagram #2)
    # ────────────────────────────────────────────────

    def process_payment(
        self,
        booking: Booking,
        phone_number: str,
        payment_method: PaymentMethod,
        coupon_code: Optional[str] = None
    ):
        """
        Full flow:
        Find member → calculate discounts → create payment → call pay()
        If success → confirm booking & generate tickets
        """

        # 1) Base price
        base_price = booking.base_price

        # 2) Find member (optional)
        member = self.park.findMemberByPhoneNumber(phone_number)

        member_discount_percent = 0
        coupon_discount = 0

        # 3) Member discount
        if member:
            member_discount_percent = member.calculateDiscount(base_price)

            # 4) If coupon present
            if coupon_code:
                coupon_discount = member.useCoupon(coupon_code, base_price)

        # 5) Calculate final price (member % + group % + feeding tickets + coupon)
        final_price = booking.calculate_final_price(
            member_discount_percent=member_discount_percent,
            coupon_discount=coupon_discount
        )

        # 6) Create a payment transaction
        payment = booking.create_payment(payment_method)

        # 7) Try to pay
        result = payment.pay(final_price)

        # 8) Payment status check
        if result:
            payment.updateStatus("Success")
            tickets = booking.confirm_booking()
            return tickets
        else:
            payment.updateStatus("Failed")
            raise Exception("Payment failed")

    # ────────────────────────────────────────────────
    # Cancel Booking
    # ────────────────────────────────────────────────

    def cancel_booking(self, booking: Booking):
        """
        Cancel booking before payment.
        """
        booking.cancel()

    # ────────────────────────────────────────────────
    # Refund
    # ────────────────────────────────────────────────

    def refund_booking(self, booking: Booking):
        """
        Refund booking after payment.
        """
        booking.refund()
