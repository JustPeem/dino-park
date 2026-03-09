from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

from api.bootstrap import build_park_from_seed
from models.users import Member

SEED_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_seed_data.json"
park = build_park_from_seed(SEED_PATH)
mcp = FastMCP("dino-park")

ROLE_MEMBER = "member"
ROLE_TICKET_STAFF = "ticket_staff"
ROLE_MANAGER = "manager"
ROLE_RANGER = "ranger"

ACTOR_ROLES = {ROLE_MEMBER, ROLE_TICKET_STAFF, ROLE_MANAGER, ROLE_RANGER}

current_session: dict[str, str] | None = None


def _deny(message: str) -> dict:
    return {"status": "error", "message": message}


def _require_login(*allowed_roles: str) -> dict | None:
    if current_session is None:
        return _deny("Please login first")

    actor_type = current_session.get("actor_type")
    if actor_type not in allowed_roles:
        return _deny(f"Role '{actor_type}' is not allowed for this action")
    return None


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
def list_actors() -> dict:
    members = [
        {
            "actor_type": ROLE_MEMBER,
            "actor_id": member.user_id,
            "name": member.name,
        }
        for member in park.list_members()
    ]
    staffs = [
        {
            "actor_type": staff.role,
            "actor_id": staff.staff_id,
            "name": staff.name,
        }
        for staff in park.list_staff()
        if getattr(staff, "role", "") in ACTOR_ROLES
    ]
    return {"status": "success", "actors": members + staffs}


@mcp.tool()
def login(actor_type: str, actor_id: str) -> dict:
    global current_session

    actor_type = actor_type.strip().lower()
    actor_id = actor_id.strip()
    if actor_type not in ACTOR_ROLES:
        return _deny("Invalid actor_type. Use member, ticket_staff, manager, or ranger")
    if not actor_id:
        return _deny("actor_id is required")

    if actor_type == ROLE_MEMBER:
        member = park.get_user_by_id(actor_id)
        if member is None:
            return _deny("Member not found")
        current_session = {
            "actor_type": ROLE_MEMBER,
            "actor_id": member.user_id,
            "name": member.name,
            "phone_number": member.phone_number,
        }
        return {"status": "success", "session": current_session}

    staff = park.get_staff_by_id(actor_id)
    if staff is None:
        return _deny("Staff not found")
    if getattr(staff, "role", "") != actor_type:
        return _deny(f"Staff {actor_id} is not a {actor_type}")

    current_session = {
        "actor_type": actor_type,
        "actor_id": actor_id,
        "name": staff.name,
    }
    return {"status": "success", "session": current_session}



@mcp.tool()
def logout() -> dict:
    global current_session
    current_session = None
    return {"status": "success", "message": "Logged out"}


@mcp.tool()
def check_seat_availability(zone_id: str, round_id: str) -> dict:
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF, ROLE_MANAGER)
    if denied is not None:
        return denied
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
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF)
    if denied is not None:
        return denied

    session = current_session or {}
    if session.get("actor_type") == ROLE_MEMBER:
        member = park.get_user_by_id(session.get("actor_id", ""))
        if member is None:
            return _deny("Member session invalid")
        phone_number = member.phone_number
    else:
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
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF, ROLE_MANAGER)
    if denied is not None:
        return denied
    return park.cancel_booking(booking_id)

@mcp.tool()
def get_round_details(zone_id: str) -> dict:
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF, ROLE_MANAGER)
    if denied is not None:
        return denied
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
    denied = _require_login(ROLE_TICKET_STAFF)
    if denied is not None:
        return denied
    return park.check_in(ticket_id)


@mcp.tool()
def create_trip(zone_id: str, vehicle_id: str, driver_license_id: str, start_time: str, end_time: str) -> dict:
    denied = _require_login(ROLE_MANAGER)
    if denied is not None:
        return denied

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
    denied = _require_login(ROLE_RANGER)
    if denied is not None:
        return denied
    return park.request_food_refill(zone_id)


@mcp.tool()
def approve_food_refill(zone_id: str) -> dict:
    denied = _require_login(ROLE_MANAGER)
    if denied is not None:
        return denied
    return park.request_food_refill(zone_id)


@mcp.tool()
def add_coupon_to_member(member_id: str) -> dict:
    denied = _require_login(ROLE_TICKET_STAFF)
    if denied is not None:
        return denied

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
    denied = _require_login(ROLE_MANAGER)
    if denied is not None:
        return denied

    from datetime import date

    return {"date": str(date.today()), "visitor_count": park.get_daily_visitor_count(date.today())}


@mcp.resource("report://food")
def food_report() -> dict:
    denied = _require_login(ROLE_MANAGER, ROLE_RANGER)
    if denied is not None:
        return denied

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
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF, ROLE_MANAGER, ROLE_RANGER)
    if denied is not None:
        return denied

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