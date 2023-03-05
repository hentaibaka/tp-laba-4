from enum import Enum, auto
from mimesis import Generic, locales
from random import choices, randrange

class StudentIDStatus(Enum):
    Overdue = auto()
    Actual = auto()

    def __repr__(self) -> str:
        return f"Student ID status: {self.name}"
    
    def __format__(self, format_spec: str) -> str:
        return self.name
    
    def __str__(self) -> str:
        return self.name

class StudentID:
    def __init__(self, status: StudentIDStatus) -> None:
        self._status = status

    @property
    def status(self) -> StudentIDStatus:
        return self._status
    
    @status.setter
    def status(self, newStatus: StudentIDStatus) -> None:
        self._status = newStatus
    
    def __repr__(self) -> str:
        return self._status.__str__()

class Bag:
    def __init__(self, bagSize: tuple[float]) -> None:
        self.__w, self.__l, self.__h = bagSize 
    
    @property
    def volume(self) -> float:
        return self.__w * self.__h * self.__l
    
    def __repr__(self) -> str:
        return f"width: {self.__w} | height: {self.__h} | lenght: {self.__l} | volume: {self.volume}"

class Student:
    def __init__(self, name: str, bag: Bag, studentID: StudentID) -> None:
        self._name = name
        self._studentID = studentID
        self._bag = bag
    
    @property
    def name(self) -> str:
        return self._name

    @property
    def studentID(self) -> StudentID:
        return self._studentID
    
    @property
    def bag(self) -> Bag:
        return self._bag
    
    @bag.setter
    def bag(self, newBag) -> None:
        self._bag = newBag

    def __repr__(self) -> str:
        return f"Student name: {self.name} | Bag: {self.bag} | Student ID: {self.studentID}"
    
class StudentGenerator:
    STUDENTIDSTATUSES = (None, *StudentIDStatus)

    def __init__(self) -> None:
        self.generic = Generic(locale=locales.Locale.RU)

    def generate(self):
        bag = choices([False, True], weights=[30, 70])[0]
        id = choices(self.STUDENTIDSTATUSES, weights=[10, 45, 45])[0]

        bag = Bag([randrange(10, 20) for _ in range(3)]) if bag else None
        if not id is None: id = StudentID(id)

        student = Student(self.generic.person.name(), bag, id)

        return student
    
