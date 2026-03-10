from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.bootstrap import build_park_from_seed
from models.users import Member

app = FastAPI(title="Dino Park API", version="1.1.0")

SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_seed_data.json"
park = build_park_from_seed(SEED_PATH)

class CreateBookingRequest(BaseModel):
    name: str
    phone_number: str
    zone_id: str
    round_id: str
    trip_id: str
    seats: int = Field(ge=1, le=10)
    coupon_code: str | None = None
    payment_channel: str = "cash"


class CheckinRequest(BaseModel):
    ticket_id: str


class StaffCouponRequest(BaseModel):
    member_id: str


class CreateTripRequest(BaseModel):
    zone_id: str
    vehicle_id: str
    driver_license_id: str
    start_time: datetime
    end_time: datetime


class FoodRefillRequest(BaseModel):
    zone_id: str


@app.get("/bookings/availability")
def check_booking_availability(zone_id: str, round_id: str):
    result = park.check_available_seats(zone_id, round_id)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@app.post("/bookings/")
def create_booking(payload: CreateBookingRequest):
    member = park.find_member_by_phone_number(payload.phone_number)
    print(f"Member found: {member}")

    zone = park.get_zone(payload.zone_id)
    print(f"Zone found: {zone}")
    if zone is None:
        raise HTTPException(status_code=404, detail="Zone not found")

    round_obj = zone.get_round(payload.round_id)
    print(f"Round object: {round_obj}")
    if round_obj is None:
        raise HTTPException(status_code=404, detail="Round not found")

    if round_obj.get_trip(payload.trip_id) is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if member is None:
        member = park.register_member(payload.name, payload.phone_number)

    booking_result = park.book_trip(
        user_id=member.user_id,
        zone_id=payload.zone_id,
        round_id=payload.round_id,
        trip_id=payload.trip_id,
        seats=payload.seats,
        base_price=round_obj.price_per_seat,
    )
    if booking_result["status"] != "success":
        raise HTTPException(status_code=400, detail=booking_result["message"])

    payment_result = park.process_payment(
        booking_id=booking_result["booking_id"],
        phone_number=payload.phone_number,
        coupon_code=payload.coupon_code,
        payment_channel=payload.payment_channel,
    )
    if payment_result["status"] != "success":
        raise HTTPException(status_code=400, detail=payment_result["message"])

    return {
        "status": "success",
        "booking_id": booking_result["booking_id"],
        "ticket_ids": [ticket.ticket_id for ticket in payment_result["tickets"]],
    }


@app.get("/bookings/{booking_id}")
def get_booking_detail(booking_id: str):
    booking = park.get_booking(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    return {
        "booking_id": booking.booking_id,
        "status": booking.status,
        "seats": booking.seats,
        "total_price": booking.total_price,
        "ticket_ids": [ticket.ticket_id for ticket in booking.tickets],
    }


@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: str):
    result = park.cancel_booking(booking_id)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/staff/checkin")
def check_in_visitor(payload: CheckinRequest):
    result = park.check_in(payload.ticket_id)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result.get("message", "Check-in failed"))
    return result


@app.post("/staff/coupon")
def add_coupon_to_member(payload: StaffCouponRequest):
    result = park.issue_food_coupon(payload.member_id)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    return {
        "status": "success",
        "coupon_code": result["coupon"].coupon_code,
        "discount": result["coupon"].discount_amount,
    }


@app.post("/trips/")
def create_trip(payload: CreateTripRequest):
    result = park.create_trip(
        zone_id=payload.zone_id,
        vehicle_key=payload.vehicle_id,
        driver_key=payload.driver_license_id,
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])

    return {"status": "success", "trip_id": result["trip"].trip_id}


@app.post("/food/refill-request")
def request_food_refill(payload: FoodRefillRequest):
    result = park.request_food_refill(payload.zone_id)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/food/approve-refill")
def approve_food_refill(payload: FoodRefillRequest):
    result = park.request_food_refill(payload.zone_id)
    if result["status"] != "success":
        raise HTTPException(status_code=400, detail=result["message"])
    return {"status": "success", "message": "Refill approved and completed"}


@app.get("/reports/daily")
def daily_report(query_date: date | None = None):
    if query_date is None:
        query_date = date.today()
    return {"date": query_date, "visitor_count": park.get_daily_visitor_count(query_date)}


@app.get("/reports/food")
def food_report():
    items = []
    for zone in park.zones:
        for cage in zone.get_cages():
            foods = cage.get_foods()
            items.append(
                {
                    "zone_id": zone.zone_id,
                    "cage_id": cage.cage_id,
                    "food_items": len(foods),
                    "expired_items": sum(1 for food in foods if food.is_expired()),
                }
            )
    return {"status": "success", "items": items}


@app.get("/reports/zones")
def zone_report():
    zones = []
    for zone in park.zones:
        zones.append(
            {
                "zone_id": zone.zone_id,
                "zone_type": zone.zone_type,
                "round_ids": [round_obj.round_id for round_obj in zone.rounds],
                "is_open": zone.check_availability(None, None),
            }
        )
    return {"status": "success", "zones": zones}