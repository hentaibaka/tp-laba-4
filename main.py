from StudentGenerator import *
from UniversityCorpus import *

if __name__ == "__main__":
    system('cls')

    MODE = 0
    STUDENTCOUNT = 12

    COLORS = ['red', 'blue', 'green', 'white']
    CORPUSES = [UniversityCorpus("ИКИТ"), UniversityCorpus("ИНиГ"), 
                UniversityCorpus("ПолиТех"), UniversityCorpus("ИСИ")]
    GENERATOR = getStudentTriesToEnterGenerator(StudentGenerator().generate, STUDENTCOUNT, CORPUSES)
    CAMPUS = UniversityCampus(CORPUSES, COLORS, GENERATOR)

    if MODE == 0:
        CAMPUS.handler = singleThreadStudentHandler
    elif MODE == 1:
        CAMPUS.handler = multiThreadStudentHandler
    elif MODE == 2:
        CAMPUS.handler = singleThreadStudentHandler

    CAMPUS.run()

    students = [log.student.name for log in CAMPUS.logs]
    studentBags = [log.student.bag.volume if log.student.bag else log.student.bag for log in CAMPUS.logs]
    studentIDs = [log.student.studentID for log in CAMPUS.logs]
    corpuses = [log.corpus for log in CAMPUS.logs]
    statuses = [log.status for log in CAMPUS.logs]

    logs = pd.DataFrame(zip(students, studentBags, studentIDs, corpuses, statuses), 
                        columns=["student name", "bag vol.", "ID", "corpus", "status"], )
    print("logs:", logs, sep="\n")

    print("max bag:", CAMPUS.maxBag, sep="\n")

    studentswByID = [log.student for log in CAMPUS.withoutStudentID]

    print("without IDs:", *studentswByID, sep="\n")