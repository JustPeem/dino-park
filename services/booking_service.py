"""Service for creating bookings and managing booking lifecycle."""

from __future__ import annotations

from typing import Optional

from models.booking import Booking
from models.payment import PaymentMethod
from models.park import Park
from models.users import MEMBER_DISCOUNT_RATE, Member


class BookingService:
    """Coordinate booking creation, payment, cancellation and refunds."""

    def __init__(self, park: Park):
        self.park = park

    def create_booking(
        self,
        user_id: str,
        zone_id: str,
        round_id: str,
        trip_id: str,
        seats: int,
    ) -> Booking:
        zone = self.park.get_zone(zone_id)
        if zone is None:
            raise ValueError("Zone not found")

        round_ref = zone.get_round(round_id)
        if round_ref is None:
            raise ValueError("Round not found")

        trip = round_ref.get_trip(trip_id)
        if trip is None:
            raise ValueError("Trip not found")

        if not trip.check_seat_availability(seats):
            raise ValueError("Not enough seats")

        user = self.park.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        trip.reserve_seats(seats)

        booking = Booking(
            user=user,
            round_ref=round_ref,
            trip=trip,
            seats=seats,
            base_price=round_ref.price_per_seat,
        )
        return booking

    def process_payment(
        self,
        booking: Booking,
        phone_number: str,
        payment_method: PaymentMethod,
        coupon_code: Optional[str] = None,
    ):
        member: Optional[Member] = self.park.find_member_by_phone_number(phone_number)

        member_discount_percent = MEMBER_DISCOUNT_RATE * 100 if member else 0
        coupon_discount = member.use_coupon(coupon_code) if member and coupon_code else 0

        final_price = booking.calculate_final_price(
            member_discount_percent=member_discount_percent,
            coupon_discount=coupon_discount,
        )

        payment = booking.create_payment(payment_method)
        result = payment.pay(final_price)

        if result:
            payment.updateStatus("Success")
            return booking.confirm_booking()

        payment.updateStatus("Failed")
        raise RuntimeError("Payment failed")

    def cancel_booking(self, booking: Booking) -> None:
        booking.cancel()

    def refund_booking(self, booking: Booking) -> None:
        booking.refund()