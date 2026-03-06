from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.park_service import service



def ok(result: Any) -> dict[str, Any]:
    return {"ok": True, "result": result}


def err(message: str) -> dict[str, Any]:
    return {"ok": False, "error": message}


def _report_daily(_: dict[str, Any]) -> dict[str, Any]:
    return service.report_daily()


def _report_food(_: dict[str, Any]) -> dict[str, Any]:
    return service.report_food()


def _report_zones(_: dict[str, Any]) -> list[dict[str, Any]]:
    return service.report_zones()


TOOLS: dict[str, Callable[[dict[str, Any]], Any]] = {
    "check_seat_availability": lambda a: service.check_seat_availability(a["trip_id"], a["seats"]),
    "create_booking": lambda a: service.create_booking(
        phone_number=a["phone_number"],
        trip_id=a["trip_id"],
        seats=a["seats"],
        payment_method=a["payment_method"],
        coupon_code=a.get("coupon_code"),
    ),
    "cancel_booking": lambda a: service.cancel_booking(a["booking_id"]),
    "check_in_ticket": lambda a: service.check_in_ticket(a["booking_id"]),
    "create_trip": lambda a: service.create_trip(
        trip_id=a["trip_id"],
        zone_id=a["zone_id"],
        round_id=a["round_id"],
        total_seats=a["total_seats"],
    ),
    "request_food_refill": lambda a: service.request_food_refill(
        zone_id=a["zone_id"],
        cage_id=a["cage_id"],
        food_name=a["food_name"],
        requested_qty=a["requested_qty"],
    ),
    "approve_food_refill": lambda a: service.approve_food_refill(a["request_id"]),
    "add_coupon_to_member": lambda a: service.add_coupon_to_member(a["member_phone"], a["coupon_code"]),
}

RESOURCES: dict[str, Callable[[dict[str, Any]], Any]] = {
    "report://daily": _report_daily,
    "report://food": _report_food,
    "park://zones": _report_zones,
}


def handle_command(payload: dict[str, Any]) -> dict[str, Any]:
    action = payload.get("action")
    if action == "list_tools":
        return ok({"tools": list(TOOLS.keys())})
    if action == "list_resources":
        return ok({"resources": list(RESOURCES.keys())})
    if action == "call_tool":
        name = payload.get("name")
        args = payload.get("arguments", {})
        if name not in TOOLS:
            return err(f"Unknown tool: {name}")
        try:
            return ok(TOOLS[name](args))
        except Exception as exc:  # noqa: BLE001
            return err(str(exc))
    if action == "read_resource":
        uri = payload.get("uri")
        if uri not in RESOURCES:
            return err(f"Unknown resource: {uri}")
        return ok(RESOURCES[uri]({}))
    return err("Unknown action")


def run_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
            response = handle_command(payload)
        except json.JSONDecodeError:
            response = err("Input must be JSON")
        sys.stdout.write(json.dumps(response, default=lambda o: o.__dict__) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_stdio()