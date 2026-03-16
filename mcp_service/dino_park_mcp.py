from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP

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
    """
    List all available actors that can login to the Dino Park system.

    This includes:
    - Members (park visitors)
    - Ticket staff
    - Rangers
    - Managers

    Returns:
        dict: {
            "status": "success",
            "actors": [
                {
                    "actor_type": str,
                    "actor_id": str,
                    "name": str
                }
            ]
        }

    Typical Workflow:
        Call this tool before `login` to discover available actors.
    """

    members = [
        {
            "actor_type": ROLE_MEMBER,
            "actor_id": member.user_id,
            "name": member.name,
        }
        for member in park.list_members()
    ]
    staffs = []
    for staff in park.list_staff():
        role = getattr(staff, "role", "")
        if role not in ACTOR_ROLES:
            continue
        staffs.append(
            {
                "actor_type": role,
                "actor_id": staff.staff_id,
                "name": staff.name,
            }
        )
    return {"status": "success", "actors": members + staffs}


@mcp.tool()
def login(actor_type: str, actor_id: str) -> dict:
    """
    Login to the Dino Park system as a specific actor.

    The login session will determine which tools and resources
    the user is allowed to access.

    Args:
        actor_type: Type of actor. One of:
            - member
            - ticket_staff
            - ranger
            - manager
        actor_id: Unique identifier of the actor.

    Returns:
        dict: Session information if login succeeds.

    Example:
        login("member", "M-001")

    Workflow:
        list_actors -> login -> use tools
    """

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
    """
    Logout from the current session.

    Clears the active user session.

    Returns:
        dict: success message.
    """
    global current_session
    current_session = None
    return {"status": "success", "message": "Logged out"}


@mcp.tool()
def check_seat_availability(zone_id: str, round_id: str) -> dict:
    """
    Check available seats for all trips in a specific zone round.

    Args:
        zone_id: Zone identifier.
        round_id: Round identifier.

    Returns:
        dict: Available seat information for each trip.

    Access:
        member
        ticket_staff
        manager

    Typical Workflow:
        for member:
        login -> get_round_details -> check_seat_availability -> create_booking -> process_payment
    """
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
    wants_food_ticket: bool = False,
) -> dict:
    """
    Reserve seats for a Dino Park tour trip (without payment).

    Creates a pending booking that must be confirmed via `process_payment`.

    Args:
        name: Visitor name.
        phone_number: Visitor phone number.
        zone_id: Zone identifier.
        round_id: Round identifier.
        trip_id: Trip identifier.
        seats: Number of seats to book.
        wants_food_ticket: Add feeding ticket for all booked seats (+67 THB per seat).

    Returns:
        dict:
        {
            "status": "success",
            "booking_id": str,
            "total_price": float,
            "wants_food_ticket": bool
        }

    Access:
        member
        ticket_staff

    Workflow:
        check_seat_availability -> create_booking -> process_payment
    """
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

    booking_result = park.book_trip(
        member.user_id,
        zone_id,
        round_id,
        trip_id,
        seats,
        round_obj.price_per_seat,
        wants_food_ticket=wants_food_ticket,
    )
    if booking_result["status"] != "success":
        return booking_result

    return {
        "status": "success",
        "booking_id": booking_result["booking_id"],
        "total_price": booking_result["booking"].total_price,
        "wants_food_ticket": booking_result["booking"].wants_food_ticket,
    }


@mcp.tool()
def process_payment(
    booking_id: str,
    coupon_code: str | None = None,
    payment_channel: str = "cash",
) -> dict:
    """
    Process payment for an existing booking and issue tickets.

    Must be called after `create_booking` to confirm the reservation.

    Args:
        booking_id: Booking identifier returned from `create_booking`.
        coupon_code: Optional discount coupon code.
        payment_channel: Payment method (default: cash).

    Returns:
        dict:
        {
            "status": "success",
            "booking_id": str,
            "ticket_ids": list[str],
            "total_price": float
        }

    Access:
        member
        ticket_staff

    Workflow:
        create_booking -> process_payment -> receive tickets
    """
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF)
    if denied is not None:
        return denied

    session = current_session or {}

    # Resolve phone number for payment
    if session.get("actor_type") == ROLE_MEMBER:
        member = park.get_user_by_id(session.get("actor_id", ""))
        if member is None:
            return _deny("Member session invalid")
        phone_number = member.phone_number
    else:
        # For ticket_staff, look up the booking to find the member's phone
        booking = park.get_booking(booking_id)
        if booking is None:
            return {"status": "error", "message": "Booking not found"}
        member = park.get_user_by_id(booking.user_id)
        if member is None:
            return {"status": "error", "message": "Member not found for booking"}
        phone_number = member.phone_number

    payment_result = park.process_payment(
        booking_id=booking_id,
        phone_number=phone_number,
        coupon_code=coupon_code,
        payment_channel=payment_channel,
    )
    if payment_result["status"] != "success":
        return payment_result

    return {
        "status": "success",
        "booking_id": booking_id,
        "ticket_ids": [ticket.ticket_id for ticket in payment_result["tickets"]],
        "total_price": payment_result.get("total_price"),
    }


@mcp.tool()
def cancel_booking(booking_id: str) -> dict:
    """
    Cancel an existing booking.

    Args:
        booking_id: Booking identifier.

    Returns:
        dict: Cancellation result.

    Access:
        member
        ticket_staff
        manager
    """
    denied = _require_login(ROLE_MEMBER, ROLE_TICKET_STAFF, ROLE_MANAGER)
    if denied is not None:
        return denied
    return park.cancel_booking(booking_id)


@mcp.tool()
def get_round_details(zone_id: str) -> dict:
    """
    Get detailed round schedule for a zone.

    Includes:
    - round start/end time
    - ticket price
    - trip information
    - assigned vehicle and driver

    Args:
        zone_id: Zone identifier.

    Returns:
        dict: Round and trip information.

    Access:
        member
        ticket_staff
        manager
    """
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
    """
    Check-in a visitor ticket when entering the park tour.

    This validates the ticket and marks it as used.

    Args:
        ticket_id: Ticket identifier.

    Returns:
        dict: Check-in result.

    Access:
        ticket_staff
    """
    denied = _require_login(ROLE_TICKET_STAFF)
    if denied is not None:
        return denied
    return park.check_in(ticket_id)


@mcp.tool()
def create_food_ticket_payment(
    member_id: str,
    zone_id: str,
    quantity: int = 1,
    payment_channel: str = "cash",
) -> dict:
    """
    Purchase food feeding ticket(s) for a park member.

    Ticket staff can sell additional food tickets to visitors
    who want to feed the dinosaurs in a specific zone.

    Args:
        member_id: Member identifier.
        zone_id: Zone identifier where feeding will take place.
        quantity: Number of food tickets to purchase (default: 1).
        payment_channel: Payment method (default: cash).

    Returns:
        dict:
        {
            "status": "success",
            "food_ticket_ids": list[str],
            "total_price": float,
            "zone_id": str
        }

    Access:
        ticket_staff

    Workflow:
        login (ticket_staff) -> create_food_ticket_payment -> hand tickets to visitor
    """
    denied = _require_login(ROLE_TICKET_STAFF)
    if denied is not None:
        return denied

    member = park.get_user_by_id(member_id)
    if member is None:
        return _deny("Member not found")

    zone = park.get_zone(zone_id)
    if zone is None:
        return {"status": "error", "message": "Zone not found"}

    result = park.purchase_food_tickets(
        member_id=member_id,
        zone_id=zone_id,
        quantity=quantity,
        payment_channel=payment_channel,
    )
    if result.get("status") != "success":
        return result

    return {
        "status": "success",
        "food_ticket_ids": result["food_ticket_ids"],
        "total_price": result["total_price"],
        "zone_id": zone_id,
    }


@mcp.tool()
def create_trip(zone_id: str, vehicle_id: str, driver_license_id: str, start_time: str, end_time: str) -> dict:
    """
    Create a new tour trip for a specific zone.

    The manager assigns a vehicle and driver to operate the trip.

    Args:
        zone_id: Zone identifier.
        vehicle_id: Vehicle identifier.
        driver_license_id: Ranger/driver identifier.
        start_time: Trip start time (ISO format).
        end_time: Trip end time (ISO format).

    Returns:
        dict:
        {
            "status": "success",
            "trip_id": str
        }

    Access:
        manager
    """
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
def create_new_round(zone_id: str, start_time: str, end_time: str, price_per_seat: float) -> dict:
    """
    Create a new round schedule for a specific zone.

    The manager defines the round time and ticket price.

    Args:
        zone_id: Zone identifier.
        start_time: Round start time (ISO format).
        end_time: Round end time (ISO format).
        price_per_seat: Ticket price per seat.

    Returns:
        dict:
        {
            "status": "success",
            "round_id": str
        }

    Access:
        manager
    """
    denied = _require_login(ROLE_MANAGER)
    if denied is not None:
        return denied

    # Validate zone exists
    zone = park.get_zone(zone_id)
    if zone is None:
        return {"status": "error", "message": "Zone not found"}

    # Validate price
    if price_per_seat <= 0:
        return {"status": "error", "message": "Price per seat must be greater than 0"}

    try:
        from datetime import datetime
        
        # Parse ISO format times
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        
        # Validate times
        if start_dt >= end_dt:
            return {"status": "error", "message": "Start time must be before end time"}
        
        result = park.create_round(
            zone_id=zone_id,
            start_time=start_dt,
            end_time=end_dt,
            price_per_seat=price_per_seat,
        )
        
        if result.get("status") == "success":
            return {"status": "success", "round_id": result["round"].round_id}
        
        return result
        
    except ValueError as e:
        return {"status": "error", "message": f"Invalid datetime format: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to create round: {str(e)}"}


@mcp.tool()
def request_food_refill(zone_id: str) -> dict:
    """
    Request food refill for dinosaurs in a zone.

    Rangers monitor food levels and request refills when needed.

    Args:
        zone_id: Zone identifier.

    Returns:
        dict: Request status.

    Access:
        ranger
    """
    denied = _require_login(ROLE_RANGER)
    if denied is not None:
        return denied
    return park.request_food_refill(zone_id)


@mcp.tool()
def approve_food_refill(zone_id: str) -> dict:
    """
    Approve a food refill request for a dinosaur zone.

    Managers approve ranger requests to refill food supplies.

    Args:
        zone_id: Zone identifier.

    Returns:
        dict: Approval result.

    Access:
        manager
    """
    denied = _require_login(ROLE_MANAGER)
    if denied is not None:
        return denied
    return park.request_food_refill(zone_id)


@mcp.resource("report://daily")
def daily_report() -> dict:
    """
    Daily visitor report.

    Provides the number of visitors that entered the park today.

    Returns:
        dict:
        {
            "date": str,
            "visitor_count": int
        }

    Access:
        manager
    """
    denied = _require_login(ROLE_MANAGER)
    if denied is not None:
        return denied

    from datetime import date

    return {"date": str(date.today()), "visitor_count": park.get_daily_visitor_count(date.today())}


@mcp.resource("report://food")
def food_report() -> dict:
    """
    Dinosaur food inventory report.

    Shows the number of food items available in each cage.

    Returns:
        dict:
        {
            "status": "success",
            "items": [
                {
                    "zone_id": str,
                    "cage_id": str,
                    "food_items": int
                }
            ]
        }

    Access:
        manager
        ranger
    """
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
    """
    Retrieve all park zones and their available rounds.

    Useful for exploring the park structure before booking tours.

    Returns:
        dict:
        {
            "zones": [
                {
                    "zone_id": str,
                    "zone_type": str,
                    "round_ids": list[str]
                }
            ]
        }

    Access:
        member
        ticket_staff
        manager
        ranger
    """
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