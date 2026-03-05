from __future__ import annotations
from datetime import datetime

class Food:
    def __init__(self, food_type: str, expiry_date: datetime):
        self.__food_type = food_type
        self.__expiry_date = expiry_date

    @property
    def food_type(self) -> str:
        return self.__food_type
    
    @classmethod
    def create(cls, food_type: str, expiry_date: datetime) -> "Food":
        return cls(food_type, expiry_date)
    
    def is_expired(self) -> bool:
        return datetime.now() > self.__expiry_date
    
    def __repr__(self) -> str:
        return f"Food(type={self.__food_type!r}, expiry={self.__expiry_date.date()})"