from __future__ import annotations


class Dino:
    def __init__(self, dino_id: str, species: str, food_source: str):
        self.__dino_id = dino_id
        self.__species = species
        self.__food_source = food_source  # maps to 'Food Sources' in class diagram

    @property
    def food_source(self) -> str:
        """
        The food type this dinosaur eats.
        Called as getFoodSource() in the Ranger-Request-Food-Refill sequence.
        """
        return self.__food_source

    def __repr__(self) -> str:
        return f"Dino(id={self.__dino_id}, species={self.__species!r}, food={self.__food_source!r})"