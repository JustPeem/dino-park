from .staff import Staff
from .member import Member
from .payment import Payment
from .zone import Zone
class Park:
    def __init__(self,name):
        self.__name = name
        self.__staffs:list[Staff] = []
        self.__members:list[Member] = []
        self.__payments:list[Payment] = []
        self.__zones:list[Zone] = []

    

