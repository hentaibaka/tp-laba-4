from typing import Any
from StudentGenerator import *
from termcolor import colored
from threading import Thread
from threading import Lock as LockThreads, Semaphore as SemLock
from multiprocessing import Process
from multiprocessing import Lock as LockProcesses
import numpy as np
from queue import Queue
from collections.abc import Callable, Iterable, Mapping


class singleThreadStudentHandler:
    def __init__(self, corpuses: list[any], colors: list[str]) -> None:
        self.__corpuses = corpuses
        self.__colors = colors
        self.__coloredCorpuses = zip(self.__colors, self.__corpuses)
        self._tryEnterCorpusDict = {campus: (campus.tryEnter, color) for color, campus in self.__coloredCorpuses}

    def tryEnter(self, student: Student, corpus: Any) -> None:
        res = self._tryEnterCorpusDict[corpus][0](student)

        print(colored(res.info, self._tryEnterCorpusDict[corpus][1]))
        corpus.logs.append(res)
    
    def release(self):
        pass

class TryEnterThread(Thread):
    def __init__(self, queue: Queue, locker, color, 
                 group: None = None, target: Callable[..., object] | None = None, 
                 name: str | None = None, args: Iterable[Any] = ..., 
                 kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.daemon = True      
        self.queue = queue
        self.target = target
        self.locker = locker
        self.color = color
    
    def run(self):
        while True:
            val = self.queue.get()
            if val is None:
                return
            else:
                res = self.target(val)

                if self.locker: self.locker.acquire()

                print(colored(res.info, self.color))
                res.corpus.logs.append(res)

                if self.locker: self.locker.release()

class multiThreadStudentHandler(singleThreadStudentHandler):
    def __init__(self, corpuses: list[any], colors: list[str]) -> None:
        super().__init__(corpuses, colors)
        self.__locker = SemLock()
        self.__queue = Queue()
        self.__threads = {corpus: TryEnterThread(self.__queue, self.__locker, 
                                                 self._tryEnterCorpusDict[corpus][1], 
                                                 target=corpus.tryEnter) 
                                    for corpus in corpuses}

        for thread in self.__threads.values():
            thread.start()
        self._tryEnterCorpusDict = {corpus: (lambda x: self.__threads[corpus].queue.put(x), 
                                             self._tryEnterCorpusDict[corpus][1])
                                    for corpus in corpuses}

    def tryEnter(self, student: Student, corpus: Any) -> None:
        self._tryEnterCorpusDict[corpus][0](student)

    def release(self):
        for t in self.__threads.values(): t.queue.put(None)
        for t in self.__threads.values(): t.join()

class TryEntrerProcess(Process):
    def __init__(self, queue: Queue, locker, color: str, 
                 group: None = None, target: Callable[..., object] | None = None, 
                 name: str | None = None, args: Iterable[Any] = ..., 
                 kwargs: Mapping[str, Any] = ..., *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.daemon = True      
        self.queue = queue
        self.target = target
        self.locker = locker
        self.color = color

    def run(self) -> None:
        while True:
            val = self.queue.get()
            if val is None:
                return
            else:
                res = self.target(val)

                if self.locker: self.locker.acquire()

                print(colored(res.info, self.color))
                res.corpus.logs.append(res)

                if self.locker: self.locker.release()
    
class multiProcessStudentHandler(singleThreadStudentHandler):
    def __init__(self, corpuses: list[any], colors: list[str]) -> None:
        super().__init__(corpuses, colors)
        self.__locker = LockProcesses()
        self.__queue = Queue()
        self.__processes = {corpus: TryEnterThread(self.__queue, self.__locker, 
                                                   self._tryEnterCorpusDict[corpus][1], 
                                                   target = corpus.tryEnter) 
                                    for corpus in corpuses}

        for thread in self.__threads.values():
            thread.start()
        self._tryEnterCorpusDict = {corpus: (lambda x: self.__threads[corpus].queue.put(x), 
                                             self._tryEnterCorpusDict[corpus][1])
                                    for corpus in corpuses}

    def tryEnter(self, student: Student, corpus: Any) -> None:
        self._tryEnterCorpusDict[corpus][0](student)

    def release(self):
        for p in self.__processes.values(): p.queue.put(None)
        for p in self.__processes.values(): p.join()

                








class SSSStudentHandler:
    @classmethod
    def CorpusThread(cls, students: list[Student], corpus: type, color: str, locker = None) -> None:
        for student in students:
            result = corpus.tryEnter(student)

            if locker: locker.acquire()
            print(colored(result, color))
            corpus.logs.append(result)
            if locker: locker.release()

    @classmethod
    def singleThread(cls, campus: type, students: list[Student], colors: list[str]) -> None:
        corpuses = campus.corpuses
        students = [(student, *choices(corpuses)) for student in students]
        students = np.reshape(students, (-1, len(students) // len(corpuses)))

        for i, corpus in enumerate(corpuses):
            cls.CorpusThread(students[i], corpus, colors[i])

    @classmethod
    def multiThread(cls, campus: type, students: list[Student], colors: list[str]) -> None:
        corpuses = campus.corpuses
        students = np.reshape(students, (-1, len(students) // len(corpuses)))
        locker = LockThreads()

        threads = [Thread(target=cls.CorpusThread, 
                          args=(students[i], corpus, colors[i], locker)) for i, corpus in enumerate(corpuses)]

        for thread in threads: thread.start()

        for thread in threads: thread.join()

    @classmethod
    def multiProcess(cls, campus: type, students: list[Student], colors: list[str]) -> None:
        corpuses = campus.corpuses
        students = np.reshape(students, (-1, len(students) // len(corpuses)))

        locker = LockProcesses()

        processes = [Process(target=cls.CorpusThread, 
                             args=(students[i], corpus, colors[i], locker)) for i, corpus in enumerate(corpuses)]

        for process in processes: process.start()

        for process in processes: process.join()