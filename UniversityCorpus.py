from collections.abc import Callable
from StudentGenerator import *
from StudentHandler import *
from enum import Enum, auto
from termcolor import COLORS
from os import system
import pandas as pd

class StudentStatuses(Enum):
    EntryAllowed = auto()
    ForInspection = auto()

    def __repr__(self) -> str:
        return f"Student status: {self.name}"
    
    def __format__(self, format_spec: str) -> str:
        return self.name
    
    def __str__(self) -> str:
        return self.name

class UniversityCorpus:
    pass

class StudentLog:
    def __init__(self, info: str, student: Student, corpus: UniversityCorpus, status: StudentStatuses) -> None:
        self.__info = info
        self.__student = student
        self.__corpus = corpus
        self.__status = status

    @property
    def info(self) -> str:
        return self.__info
    
    @property
    def student(self) -> Student:
        return self.__student
    
    @property
    def corpus(self) -> UniversityCorpus:
        return self.__corpus
    
    @property
    def status(self) -> StudentStatuses:
        return self.__status
    
    def __repr__(self) -> str:
        return f"{self.student}, corpus: {self.corpus}, status: {self.status}"

class UniversityCorpus:
    def __init__(self, name: str) -> str:
        self._name = name
        self._logs: list[StudentLog] = []

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def logs(self) -> list[StudentLog]:
        return self._logs
    
    def tryEnter(self, student: Student) -> StudentLog:
        status = StudentStatuses.EntryAllowed

        if ((student.bag and student.bag.volume > 4000) or
             not student.studentID or (student.studentID and student.studentID.status is StudentIDStatus.Overdue)):
            status = StudentStatuses.ForInspection

        log = StudentLog((f"<==========================================>\n" +
                f"{student.name} tries to enter {self.name} corpus\n" +
                f"{student}\n" +
                f"Student status: {status}\n" +
                f"<==========================================>"),
                student, self, status)
        return log
    
    def __repr__(self) -> str:
        return self.name

class UniversityCampus:
    def __init__(self, corpuses: list[UniversityCorpus], colors: list[str],
                 studentDetector: Callable[[], Student],
                 handler: Callable[[list[UniversityCorpus], list[str]], Callable[[], None]] = None) -> None:
        self.__list = corpuses if corpuses else []
        self.__handler = handler
        self.__colors = colors
        self.__detector = studentDetector

    @property
    def logs(self) -> list[StudentLog]:
        arr = []
        for corpus in self.__list:
            for log in corpus.logs:
                arr.append(log)
        return arr
    
    @property
    def withoutStudentID(self) -> list[StudentLog]:
        return list(filter(lambda x: x.student.studentID == None or (x.student.studentID and x.student.studentID.status == StudentIDStatus.Overdue), self.logs))
    
    @property
    def maxBag(self) -> StudentLog:
        return max(self.logs, key=lambda x: x.student.bag.volume if x.student.bag else 0)

    @property
    def handler(self) -> Callable[[type, type, list[Student], list[str]], None]:
        return self.__handler
    
    @handler.setter
    def handler(self, newHandler) -> None:
        self.__handler = newHandler

    @property
    def corpuses(self) -> list:
        return self.__list
    
    @corpuses.setter
    def corpuses(self, newList) -> None:
        self.__list = newList if newList else []
    
    def run(self) -> None:
        handler = self.__handler(self.corpuses, self.__colors)
        for student, corpus in self.__detector:
            #print(student, corpus.name)
            handler.tryEnter(student, corpus)
        handler.release()

def getStudentTriesToEnterGenerator(studentGen: Callable[[], Student], countStudents: int, corpuses: UniversityCorpus) -> tuple[any]:
    for _ in range(countStudents):
        yield (studentGen(), *(choices(corpuses)))

