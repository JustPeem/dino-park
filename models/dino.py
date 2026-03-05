class Dino:
    def __init__(self,dinoId: int,food_source: str,species: str):
        self.__dinoId = dinoId
        self.__species = species
        self.__food_source = food_source

    @property
    def food_source(self) -> str:
        return self.__food_source