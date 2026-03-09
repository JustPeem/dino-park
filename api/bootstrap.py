from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from models.cage import Cage
from models.dino import Dino
from models.driver import Driver
from models.park import Park
from models.staff import Manager, Ranger, TicketStaff
from models.users import Member
from models.round import Round
from models.vehicle import Vehicle
from models.zone import Zone


def _normalize_future_time(dt: datetime) -> datetime:
    now = datetime.now()
    while dt < now:
        dt = dt + timedelta(days=1)
    return dt


def build_park_from_seed(seed_path: str | Path) -> Park:
    path = Path(seed_path)
    payload = json.loads(path.read_text(encoding="utf-8"))

    park = Park("Dino Park")

    zone_map: dict[str, Zone] = {}
    for zone_row in payload.get("zones", []):
        zone = Zone(zone_row["zone_id"], zone_row.get("name", zone_row["zone_id"]))
        zone_map[zone.zone_id] = zone
        park.add_zone(zone)

    cage_map: dict[str, Cage] = {}
    for cage_row in payload.get("cages", []):
        cage = Cage(cage_row["cage_id"])
        cage_map[cage.cage_id] = cage
        zone = zone_map.get(cage_row["zone_id"])
        if zone is not None:
            zone.add_cage(cage)

    for dino_row in payload.get("dinos", []):
        cage = cage_map.get(dino_row["cage_id"])
        if cage is None:
            continue
        cage.add_dino(Dino(dino_row["dino_id"], dino_row["species"], dino_row["food_type"]))

    for vehicle_row in payload.get("vehicles", []):
        capacity = vehicle_row.get("capacity") or vehicle_row.get("total_seats") or 0
        park.add_vehicle(Vehicle(vehicle_row["vehicle_id"], int(capacity)))

    for staff_row in payload.get("staff", []):
        role = staff_row.get("role")
        if role == "driver":
            park.add_staff(Driver(staff_row["staff_id"], staff_row["name"], staff_row["license_id"]))
        elif role == "manager":
            park.add_staff(Manager(staff_row["staff_id"], staff_row["name"]))
        elif role == "ranger":
            park.add_staff(Ranger(staff_row["staff_id"], staff_row["name"]))
        elif role == "ticket_staff":
            park.add_staff(TicketStaff(staff_row["staff_id"], staff_row["name"]))

    for member_row in payload.get("members", []):
        park.add_member(Member(member_row["name"], member_row["phone_number"], member_row["member_id"]))

    round_by_seed_key: dict[tuple[str, str], Round] = {}
    for trip_row in payload.get("trips", []):
        zone = zone_map.get(trip_row["zone_id"])
        if zone is None:
            continue

        seed_key = (trip_row["zone_id"], trip_row["round_id"])
        if seed_key not in round_by_seed_key:
            start_time = _normalize_future_time(datetime.fromisoformat(trip_row["start_time"]))
            end_time = _normalize_future_time(datetime.fromisoformat(trip_row["end_time"]))
            if end_time <= start_time:
                end_time = start_time + timedelta(hours=1)
            round_obj = Round(zone, start_time, end_time, 500.0, round_id=trip_row["round_id"])
            zone.add_round(round_obj)
            round_by_seed_key[seed_key] = round_obj

    for trip_row in payload.get("trips", []):
        zone = zone_map.get(trip_row["zone_id"])
        if zone is None:
            continue
        round_obj = round_by_seed_key.get((trip_row["zone_id"], trip_row["round_id"]))
        if round_obj is None:
            continue

        driver = None
        if "driver_id" in trip_row:
            driver = park.get_driver(trip_row["driver_id"]) or park.get_driver(trip_row.get("license_id", ""))
        if driver is None and "license_id" in trip_row:
            driver = park.get_driver(trip_row["license_id"])

        if driver is None:
            for staff in payload.get("staff", []):
                if staff.get("role") == "driver":
                    d = park.get_driver(staff["license_id"])
                    if d is not None:
                        driver = d
                        break
        if driver is None:
            continue

        park.create_trip(
            zone_id=zone.zone_id,
            vehicle_key=trip_row["vehicle_id"],
            driver_key=driver.license_id,
            start_time=round_obj.start_time,
            end_time=round_obj.end_time,
        )

    return park