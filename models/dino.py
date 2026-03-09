from __future__ import annotations


class Dino:
    def __init__(self, dino_id: str, species: str, food_source: str):
        self.__dino_id = dino_id
        self.__species = species
        self.__food_source = food_source

    @property
    def dino_id(self) -> str:
        return self.__dino_id

    @property
    def food_source(self) -> str:
        return self.__food_source

    def __repr__(self) -> str:
        return f"Dino(id={self.__dino_id}, species={self.__species!r}, food={self.__food_source!r})"