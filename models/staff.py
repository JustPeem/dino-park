from __future__ import annotations

from abc import ABC
from datetime import datetime


class Staff(ABC):
    ROLE = "staff"

    def __init__(self, staff_id: str, name: str):
        self.__staff_id = staff_id
        self.__name = name

    @property
    def staff_id(self) -> str:
        return self.__staff_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def role(self) -> str:
        return self.ROLE


class Manager(Staff):
    ROLE = "manager"

    def request_create_trip(self, park, zone_id: str, vehicle_id: str, driver_license: str, start_time: datetime, end_time: datetime):
        return park.create_trip(zone_id, vehicle_id, driver_license, start_time, end_time)


class Ranger(Staff):
    ROLE = "ranger"

    def request_food_refill(self, zone_id: str, park):
        return park.request_food_refill(zone_id)


class TicketStaff(Staff):
    ROLE = "ticket_staff"

    def check_in(self, ticket_id: str, park):
        return park.check_in(ticket_id)

    def add_feeding_ticket(self, member_id: str, park):
        return park.issue_food_coupon(member_id)