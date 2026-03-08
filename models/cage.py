from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dino import Dino
    from .food import Food


class Cage:
    def __init__(self, cage_id: str):
        self.__cage_id = cage_id
        self.__dinos: list["Dino"] = []
        self.__foods: list["Food"] = []

    @property
    def cage_id(self) -> str:
        return self.__cage_id

    def get_dinos(self) -> list["Dino"]:
        return self.__dinos

    def add_dino(self, dino: "Dino") -> None:
        self.__dinos.append(dino)

    def get_foods(self) -> list["Food"]:
        return self.__foods

    def add_food(self, food_type: str, expiry_date: datetime | None = None) -> "Food":
        from .food import Food

        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=3)
        food = Food.create(food_type, expiry_date)
        self.__foods.append(food)
        return food

    def remove_expired_food(self) -> None:
        self.__foods = [f for f in self.__foods if not f.is_expired()]

    def __repr__(self) -> str:
        return f"Cage(id={self.__cage_id!r}, dinos={len(self.__dinos)}, foods={len(self.__foods)})"