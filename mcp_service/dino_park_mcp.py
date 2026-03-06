
"""MCP server exposing Dino Park tools and resources from README."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from services.system_service import service

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover - runtime dependency guard
    raise RuntimeError("mcp package is required. Install dependencies before running MCP service.") from exc

mcp = FastMCP("dino-park")


def _run_tool(action):
    try:
        result = action()
        return json.dumps({"ok": True, "data": result}, default=str, ensure_ascii=False)
    except ValueError as exc:
        return json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False)


@mcp.tool()
def check_seat_availability(zone_id: str, round_id: str, trip_id: str, seats: int) -> str:
    return _run_tool(lambda: service.check_seat_availability(zone_id, round_id, trip_id, seats))



@mcp.tool()
def create_booking(user_id: str, zone_id: str, round_id: str, trip_id: str, seats: int) -> str:
    booking = service.create_booking(user_id, zone_id, round_id, trip_id, seats)
    return json.dumps(booking.__dict__, default=str, ensure_ascii=False)


@mcp.tool()
def cancel_booking(booking_id: str) -> str:
    return json.dumps(service.cancel_booking(booking_id), ensure_ascii=False)


@mcp.tool()
def check_in_ticket(ticket_id: str) -> str:
    return json.dumps(service.check_in_ticket(ticket_id), ensure_ascii=False)


@mcp.tool()
def create_trip(zone_id: str, vehicle_id: str, driver_id: str, start_time: str, end_time: str) -> str:
    return json.dumps(service.create_trip(zone_id, vehicle_id, driver_id, start_time, end_time), ensure_ascii=False)


@mcp.tool()
def request_food_refill(zone_id: str, ranger_id: str, food_type: str, amount: int) -> str:
    return json.dumps(service.request_food_refill(zone_id, ranger_id, food_type, amount), ensure_ascii=False)


@mcp.tool()
def approve_food_refill(request_id: str, manager_id: str) -> str:
    return json.dumps(service.approve_food_refill(request_id, manager_id), ensure_ascii=False)


@mcp.tool()
def add_coupon_to_member(member_id: str, coupon_code: str, discount_value: float, expiry_date: str) -> str:
    return json.dumps(service.add_coupon_to_member(member_id, coupon_code, discount_value, expiry_date), ensure_ascii=False)


@mcp.resource("report://daily")
def resource_daily() -> str:
    return json.dumps(service.report_daily(), ensure_ascii=False)


@mcp.resource("report://food")
def resource_food() -> str:
    return json.dumps(service.report_food(), ensure_ascii=False)


@mcp.resource("park://zones")
def resource_zones() -> str:
    return json.dumps(service.report_zones(), ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport="stdio")