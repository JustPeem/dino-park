"""Core in-memory application service aligned with README use-cases.

This module centralizes UC1-UC8 so both FastAPI and MCP expose the same behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import json
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class BookingRecord:
    booking_id: str
    user_id: str
    zone_id: str
    round_id: str
    trip_id: str
    seats: int
    total_price: float
    status: str = "PAID"
    created_at: datetime = field(default_factory=datetime.utcnow)




def _default_seed_data() -> dict[str, Any]:
    return {
        "staff": [],
        "vehicles": [],
        "zones": [],
        "cages": [],
        "dinos": [],
        "trips": [],
    }


def _load_seed_data(path: str = "data/sample_seed_data.json") -> dict[str, Any]:
    candidate_files = [Path(path), Path("data/data.json"), Path("data.json")]
    data: dict[str, Any] | None = None

    for data_file in candidate_files:
        if not data_file.exists():
            continue

        try:
            with data_file.open("r", encoding="utf-8-sig") as file:
                raw = file.read().strip()
                if not raw:
                    continue
                loaded = json.loads(raw)
                if isinstance(loaded, dict):
                    data = loaded
                    break
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue

    if data is None:
        return _default_seed_data()

    defaults = _default_seed_data()
    return {
        key: data.get(key, defaults[key]) if isinstance(data.get(key, defaults[key]), list) else defaults[key]
        for key in defaults
    }

class DinoParkService:
    """Simple in-memory implementation for API/MCP feature parity from README."""

    def __init__(self) -> None:
        self._bookings: dict[str, BookingRecord] = {}
        self._coupons: dict[str, list[dict[str, Any]]] = {}
        self._food_stock: dict[str, int] = {"herbivore": 100, "carnivore": 60}
        self._refill_requests: dict[str, dict[str, Any]] = {}

        seed = _load_seed_data()
        self._staff: dict[str, dict[str, Any]] = {item["staff_id"]: item for item in seed.get("staff", [])}
        self._vehicles: dict[str, dict[str, Any]] = {item["vehicle_id"]: item for item in seed.get("vehicles", [])}
        self._zones: dict[str, dict[str, Any]] = {item["zone_id"]: item for item in seed.get("zones", [])}
        self._cages: dict[str, dict[str, Any]] = {item["cage_id"]: item for item in seed.get("cages", [])}
        self._dinos: dict[str, dict[str, Any]] = {item["dino_id"]: item for item in seed.get("dinos", [])}
        self._trips: dict[str, dict[str, Any]] = {item["trip_id"]: item for item in seed.get("trips", [])}

    @staticmethod
    def _booking_price(seats: int) -> float:
        return float(max(0, seats) * 500)

    def check_seat_availability(self, zone_id: str, round_id: str, trip_id: str, seats: int) -> dict[str, Any]:
        trip = self._trips.get(trip_id)
        if trip is None:
            raise ValueError("Trip not found")

        if trip["zone_id"] != zone_id or trip.get("round_id") != round_id:
            raise ValueError("Trip does not match zone/round")

        booked = sum(
            booking.seats
            for booking in self._bookings.values()
            if booking.zone_id == zone_id and booking.round_id == round_id and booking.trip_id == trip_id and booking.status == "PAID"
        )
        capacity = int(trip.get("capacity", 40))
        available = capacity - booked
        return {
            "zone_id": zone_id,
            "round_id": round_id,
            "trip_id": trip_id,
            "requested": seats,
            "available": max(0, available),
            "can_book": available >= seats,
        }

    def create_booking(self, user_id: str, zone_id: str, round_id: str, trip_id: str, seats: int) -> BookingRecord:
        availability = self.check_seat_availability(zone_id, round_id, trip_id, seats)
        if not availability["can_book"]:
            raise ValueError("Not enough seats")

        booking = BookingRecord(
            booking_id=f"B-{date.today().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}",
            user_id=user_id,
            zone_id=zone_id,
            round_id=round_id,
            trip_id=trip_id,
            seats=seats,
            total_price=self._booking_price(seats),
        )
        self._bookings[booking.booking_id] = booking
        return booking

    def get_booking(self, booking_id: str) -> BookingRecord:
        if booking_id not in self._bookings:
            raise ValueError("Booking not found")
        return self._bookings[booking_id]

    def cancel_booking(self, booking_id: str) -> dict[str, Any]:
        booking = self.get_booking(booking_id)
        if booking.status == "CANCELLED":
            return {"booking_id": booking_id, "status": "CANCELLED", "refund": 0.0}

        booking.status = "CANCELLED"
        refund = booking.total_price
        return {"booking_id": booking_id, "status": booking.status, "refund": refund}

    def check_in_ticket(self, ticket_id: str) -> dict[str, Any]:
        return {"ticket_id": ticket_id, "status": "CHECKED_IN", "checked_in_at": datetime.utcnow().isoformat()}

    def add_coupon_to_member(self, member_id: str, coupon_code: str, discount_value: float, expiry_date: str) -> dict[str, Any]:
        coupon = {
            "coupon_code": coupon_code,
            "discount_value": discount_value,
            "expiry_date": expiry_date,
        }
        self._coupons.setdefault(member_id, []).append(coupon)
        return {"member_id": member_id, "coupon": coupon}

    def create_trip(self, zone_id: str, vehicle_id: str, driver_id: str, start_time: str, end_time: str) -> dict[str, Any]:
        if zone_id not in self._zones:
            raise ValueError("Zone not found")
        if vehicle_id not in self._vehicles:
            raise ValueError("Vehicle not found")
        if driver_id not in self._staff:
            raise ValueError("Staff not found")

        trip_id = f"TR-{uuid4().hex[:4].upper()}"
        trip = {
            "trip_id": trip_id,
            "zone_id": zone_id,
            "round_id": f"R-{datetime.utcnow().strftime('%H%M')}",
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "capacity": int(self._vehicles[vehicle_id].get("capacity", 40)),
            "start_time": start_time,
            "end_time": end_time,
        }
        self._trips[trip_id] = trip
        return trip

    def request_food_refill(self, zone_id: str, ranger_id: str, food_type: str, amount: int) -> dict[str, Any]:
        if zone_id not in self._zones:
            raise ValueError("Zone not found")
        if ranger_id not in self._staff:
            raise ValueError("Staff not found")

        request_id = f"FR-{uuid4().hex[:6].upper()}"
        req = {
            "request_id": request_id,
            "zone_id": zone_id,
            "ranger_id": ranger_id,
            "food_type": food_type,
            "amount": amount,
            "status": "PENDING",
        }
        self._refill_requests[request_id] = req
        return req

    def approve_food_refill(self, request_id: str, manager_id: str) -> dict[str, Any]:
        if request_id not in self._refill_requests:
            raise ValueError("Refill request not found")
        if manager_id not in self._staff:
            raise ValueError("Staff not found")

        req = self._refill_requests[request_id]
        req["status"] = "APPROVED"
        req["manager_id"] = manager_id
        self._food_stock[req["food_type"]] = self._food_stock.get(req["food_type"], 0) + req["amount"]
        return req

    def report_daily(self) -> dict[str, Any]:
        today = date.today()
        today_bookings = [
            booking for booking in self._bookings.values() if booking.created_at.date() == today and booking.status == "PAID"
        ]
        return {
            "date": today.isoformat(),
            "visitor_count": sum(booking.seats for booking in today_bookings),
            "revenue": sum(booking.total_price for booking in today_bookings),
        }

    def report_food(self) -> dict[str, Any]:
        return {"stock": self._food_stock, "pending_refills": [r for r in self._refill_requests.values() if r["status"] == "PENDING"]}

    def report_zones(self) -> dict[str, Any]:
        return {
            "zones": [
                {
                    "zone_id": zone["zone_id"],
                    "name": zone["name"],
                    "open": zone.get("open", True),
                    "cages": [c for c in self._cages.values() if c["zone_id"] == zone["zone_id"]],
                    "dino_count": sum(1 for dino in self._dinos.values() if dino["cage_id"] in {c["cage_id"] for c in self._cages.values() if c["zone_id"] == zone["zone_id"]}),
                }
                for zone in self._zones.values()
            ]
        }


_service: DinoParkService | None = None


def get_service() -> DinoParkService:
    """Return a lazily-initialized singleton service instance."""
    global _service
    if _service is None:
        _service = DinoParkService()
    return _service


service = get_service()