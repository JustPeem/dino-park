from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from api.bootstrap import build_park_from_seed
from models.users import Member

SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_seed_data.json"
park = build_park_from_seed(SEED_PATH)

mcp = FastMCP("dino-park")


def _find_round_and_trip(zone_id: str, round_id: str, trip_id: str):
    zone = park.get_zone(zone_id)
    if zone is None:
        return None, None, None
    round_obj = zone.get_round(round_id)
    if round_obj is None:
        return zone, None, None
    trip = round_obj.get_trip(trip_id)
    return zone, round_obj, trip


@mcp.tool()
def check_seat_availability(zone_id: str, round_id: str) -> dict:
    return park.check_available_seats(zone_id, round_id)


@mcp.tool()
def create_booking(
    name: str,
    phone_number: str,
    zone_id: str,
    round_id: str,
    trip_id: str,
    seats: int,
    coupon_code: str | None = None,
    payment_channel: str = "cash",
) -> dict:
    member = park.find_member_by_phone_number(phone_number)
    if member is None:
        member = Member(name, phone_number)
        park.add_member(member)

    zone, round_obj, trip = _find_round_and_trip(zone_id, round_id, trip_id)
    if zone is None:
        return {"status": "error", "message": "Zone not found"}
    if round_obj is None:
        return {"status": "error", "message": "Round not found"}
    if trip is None:
        return {"status": "error", "message": "Trip not found"}

    booking_result = park.book_trip(member.user_id, zone_id, round_id, trip_id, seats, round_obj.price_per_seat)
    if booking_result["status"] != "success":
        return booking_result

    payment_result = park.process_payment(
        booking_id=booking_result["booking_id"],
        phone_number=phone_number,
        coupon_code=coupon_code,
        payment_channel=payment_channel,
    )
    if payment_result["status"] != "success":
        return payment_result

    return {
        "status": "success",
        "booking_id": booking_result["booking_id"],
        "ticket_ids": [ticket.ticket_id for ticket in payment_result["tickets"]],
    }


@mcp.tool()
def cancel_booking(booking_id: str) -> dict:
    return park.cancel_booking(booking_id)

@mcp.tool()
def get_round_details(zone_id: str) -> dict:
    zone = park.get_zone(zone_id)
    if zone is None:
        return {"status": "error", "message": "Zone not found"}
    return {
        "status": "success",
        "rounds": [
            {
                "round_id": round_obj.round_id,
                "start_time": round_obj.start_time.isoformat(),
                "end_time": round_obj.end_time.isoformat(),
                "price_per_seat": round_obj.price_per_seat,
                "trips": [
                    {
                        "trip_id": trip.trip_id,
                        "vehicle_id": trip.vehicle.vehicle_id,
                        "driver_id": trip.driver.staff_id,
                    }
                    for trip in round_obj.trips
                ],
            }
            for round_obj in zone.rounds
        ],
    }

@mcp.tool()
def check_in_ticket(ticket_id: str) -> dict:
    return park.check_in(ticket_id)


@mcp.tool()
def create_trip(zone_id: str, vehicle_id: str, driver_license_id: str, start_time: str, end_time: str) -> dict:
    from datetime import datetime

    result = park.create_trip(
        zone_id=zone_id,
        vehicle_key=vehicle_id,
        driver_key=driver_license_id,
        start_time=datetime.fromisoformat(start_time),
        end_time=datetime.fromisoformat(end_time),
    )
    if result.get("status") == "success":
        return {"status": "success", "trip_id": result["trip"].trip_id}
    return result


@mcp.tool()
def request_food_refill(zone_id: str) -> dict:
    return park.request_food_refill(zone_id)


@mcp.tool()
def approve_food_refill(zone_id: str) -> dict:
    return park.request_food_refill(zone_id)


@mcp.tool()
def add_coupon_to_member(member_id: str) -> dict:
    result = park.issue_food_coupon(member_id)
    if result.get("status") != "success":
        return result
    return {
        "status": "success",
        "coupon_code": result["coupon"].coupon_code,
        "discount": result["coupon"].discount_amount,
    }


@mcp.resource("report://daily")
def daily_report() -> dict:
    from datetime import date

    return {"date": str(date.today()), "visitor_count": park.get_daily_visitor_count(date.today())}


@mcp.resource("report://food")
def food_report() -> dict:
    items = []
    for zone in park.zones:
        for cage in zone.get_cages():
            foods = cage.get_foods()
            items.append({
                "zone_id": zone.zone_id,
                "cage_id": cage.cage_id,
                "food_items": len(foods),
            })
    return {"status": "success", "items": items}


@mcp.resource("park://zones")
def zones_report() -> dict:
    return {
        "zones": [
            {
                "zone_id": zone.zone_id,
                "zone_type": zone.zone_type,
                "round_ids": [round_obj.round_id for round_obj in zone.rounds],
            }
            for zone in park.zones
        ]
    }


if __name__ == "__main__":
    mcp.run()