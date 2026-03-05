from __future__ import annotations
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dino import Dino
    from food import Food


class Cage:
    def __init__(self, cage_id: str):
        """
        cage_id follows format C-XXX  e.g. "C-001", "C-012"
        """
        self.__cage_id = cage_id
        self.__dinos: list["Dino"] = []
        self.__foods: list["Food"] = []

    @property
    def cage_id(self) -> str:
        return self.__cage_id
    
    def get_dinos(self) -> list["Dino"]:
        return self.__dinos

    def get_foods(self) -> list["Food"]:
        return self.__foods

    # ── Dino management ───────────────────────────────────────────────────
    def add_dino(self, dino: "Dino") -> None:
        self.__dinos.append(dino)

    def remove_dino(self, dino: "Dino") -> None:
        if dino in self.__dinos:
            self.__dinos.remove(dino)

    # ── Food management  (SD1: addFood(foodType) → Food.create()) ─────────
    def add_food(self, food_type: str,
                 expiry_date: datetime | None = None) -> "Food":
        """
        SD1: Cage receives addFood(foodType)
             → creates Food(foodType, expiryDate) directly
             ← Food created, appended to cage
        """
        from food import Food
        if expiry_date is None:
            expiry_date = datetime.now() + timedelta(days=3)
        food = Food.create(food_type, expiry_date)
        self.__foods.append(food)
        return food

    def remove_expired_food(self) -> None:
        self.__foods = [f for f in self.__foods if not f.is_expired()]

    def get_food_count_by_type(self, food_type: str) -> int:
        return sum(1 for f in self.__foods if f.food_type == food_type)


    def __repr__(self) -> str:
        return f"Cage(id={self.__cage_id!r}, dinos={len(self.__dinos)}, foods={len(self.__foods)})"