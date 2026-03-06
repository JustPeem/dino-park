"""FastAPI app exposing endpoints documented in README."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.system_service import service

app = FastAPI(title="Dino Park Management API", version="1.0.0")


class BookingRequest(BaseModel):
    user_id: str
    zone_id: str
    round_id: str
    trip_id: str
    seats: int = Field(gt=0)


class CheckinRequest(BaseModel):
    ticket_id: str


class CouponRequest(BaseModel):
    member_id: str
    coupon_code: str
    discount_value: float = Field(ge=0)
    expiry_date: str


class TripRequest(BaseModel):
    zone_id: str
    vehicle_id: str
    driver_id: str
    start_time: str
    end_time: str


class FoodRefillRequest(BaseModel):
    zone_id: str
    ranger_id: str
    food_type: str
    amount: int = Field(gt=0)


class FoodApproveRequest(BaseModel):
    request_id: str
    manager_id: str


@app.get("/bookings/availability")
def check_availability(zone_id: str, round_id: str, trip_id: str, seats: int):
    return service.check_seat_availability(zone_id, round_id, trip_id, seats)


@app.post("/bookings/")
def create_booking(payload: BookingRequest):
    try:
        booking = service.create_booking(**payload.model_dump())
        return booking.__dict__
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/bookings/{booking_id}")
def get_booking(booking_id: str):
    try:
        booking = service.get_booking(booking_id)
        return booking.__dict__
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: str):
    try:
        return service.cancel_booking(booking_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/staff/checkin")
def checkin(payload: CheckinRequest):
    return service.check_in_ticket(payload.ticket_id)


@app.post("/staff/coupon")
def issue_coupon(payload: CouponRequest):
    return service.add_coupon_to_member(**payload.model_dump())


@app.post("/trips/")
def create_trip(payload: TripRequest):
    return service.create_trip(**payload.model_dump())


@app.post("/food/refill-request")
def request_refill(payload: FoodRefillRequest):
    return service.request_food_refill(**payload.model_dump())


@app.post("/food/approve-refill")
def approve_refill(payload: FoodApproveRequest):
    try:
        return service.approve_food_refill(**payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/reports/daily")
def report_daily():
    return service.report_daily()


@app.get("/reports/food")
def report_food():
    return service.report_food()


@app.get("/reports/zones")
def report_zones():
    return service.report_zones()