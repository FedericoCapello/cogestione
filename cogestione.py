from random import shuffle
from random import randint
import matplotlib.pyplot as plt


class Session(object):
    def __init__(self, n, capacity, course):
        self.n = n
        self.capacity = capacity
        self.enrolled = 0
        self.students = []
        self.course = course

    def add(self, student):
        if student in self.students or self.enrolled == self.capacity or student.courses[(self.n + 1) % 2] == self.course:
            return False
        if True:
            self.students.append(student)
            student.courses[self.n] = self.course
            self.enrolled += 1
            return self.course

    def remove(self, student):
        if student not in self.students:
            return False
        else:
            self.students.remove(student)
            student.courses[self.n] = 0
            self.enrolled -= 1
            return self.course

    def __repr__(self):
        return self.students.__repr__()


class Course(object):
    def __init__(self, course_name, capacity):
        self.course_name = course_name
        self.capacity = capacity
        self.sessions = [Session(0, capacity, self), Session(1, capacity, self)]

    def add_student(self, student, session):
        return self.sessions[session].add(student)

    def remove_student(self, student, session):
        return self.sessions[session].remove(student)

    def __repr__(self):
        return self.course_name + ' ' + ' '.join([s.__repr__() for s in self.sessions])

    def __str__(self):
        return self.course_name

class Student(object):
    def __init__(self, name):
        self.name = name
        self.preferences = ["" for p in range(3)]
        self.broad_preferences = []
        self.happiness = 0
        self.courses = ["" for c in range(2)]

    def add_preference(self, course, rank):
        self.preferences[rank] = course

    def adjusted_preferences(self, courses):
        shuffle(courses)
        for course in courses:
            if course not in self.preferences:
                self.broad_preferences.append(course)
        for course in self.preferences:
            self.broad_preferences.insert(0, course)

    def enroll(self, course, session):
        return course.add_student(self, session)

    def un_enroll(self, session):
        return self.courses[session].remove_student(self, session)

    def compute_happiness(self):
        self.happiness = 0
        for c in self.courses:
            if c in self.preferences:
                self.happiness += 3 - self.preferences.index(c)
        return self.happiness

    def __repr__(self):
        return self.name + ' ' + ' '.join([c.__str__() for c in self.courses])


class LocalSearchSolver(object):
    def __init__(self):
        self.N = 0
        self.K = 0
        self.courses = []
        self.students = []
        self.course_dict = {}
        self.student_dict = {}
        self.happiness = 0
        self.w_1 = 1
        self.w_2 = 1.2

        self.points = []

    def construct_from_file(self):
        with open("studenti.txt", "r") as f:
            for student in f.read().split("\n"):
                self.add_student(student)

        with open("corsi.txt", "r") as f:
            for corsi in f.read().split("\n"):
                info = corsi.split(" ")
                self.add_course(info[0], int(info[1]))

        with open("preferenze.txt", "r") as f:
            for preferenza, studente in zip(f, self.students):
                info = preferenza.split(" ")
                for corso, i in zip(info, range(3)):
                    corso = corso.replace("\n", "")
                    studente.add_preference(self.course_dict[corso], 2-i)
        for student in self.students:
            student.adjusted_preferences(self.courses)
        return True

    def add_student(self, name):
        self.N += 1
        self.students.append(Student(name))
        self.student_dict[name] = self.students[-1]

    def add_course(self, course_name, capacity):
        self.K += 1
        self.courses.append(Course(course_name, capacity))
        self.course_dict[course_name] = self.courses[-1]

    def heuristic(self):
        students_happiness = [student.compute_happiness() for student in self.students]
        total_happiness = self.w_1 * float(sum(students_happiness))/float(self.N)
        equality = self.w_2 * min(students_happiness)
        unhappy_students = students_happiness.count(0)
        self.happiness = self.w_1 * total_happiness + self.w_2 * equality - 0.05 * unhappy_students
        return self.happiness

    def print_equality(self):
        students_happiness = [student.compute_happiness() for student in self.students]
        equality = self.w_2 * min(students_happiness)
        print(equality)

    def print_total(self):
        students_happiness = [student.compute_happiness() for student in self.students]
        total_happiness = self.w_1 * float(sum(students_happiness))/float(self.N)
        print(total_happiness)

    def count_0s(self):
        students_happiness = [student.compute_happiness() for student in self.students]
        print(students_happiness.count(0))

    def plot_histo(self):
        students_happiness = [student.compute_happiness() for student in self.students]
        plt.hist(students_happiness, bins=[0, 1, 2, 3, 4, 5])
        plt.show()

    def greedy_assign(self):
        shuffle(self.students)
        for student in self.students:
            i = 0
            while not student.enroll(student.broad_preferences[i], 0):
                i += 1
        for student in self.students[::-1]:
            i = 0
            while not student.enroll(student.broad_preferences[i], 1):
                i += 1

    def swap(self, student_a, session_a, student_b, session_b):
        course_a = student_a.un_enroll(session_a)
        course_b = student_b.un_enroll(session_b)
        student_a.enroll(course_b, session_a)
        student_b.enroll(course_a, session_b)
        # update 
        return True
    
    def local_search(self, iterations = 500000):
        current_happiness = self.heuristic()
        starting_happiness = current_happiness
        step = 0
        self.plot_histo()
        print(self.count_0s())
        for i in range(iterations):
            session_a = randint(0, 1)
            session_b = session_a
            student_a = self.students[randint(0, len(self.students) - 1)]
            student_b = self.students[randint(0, len(self.students) - 1)]
            if student_a.courses[(session_a + 1) % 2] != student_b.courses[session_b] and student_b.courses[(session_b + 1) % 2] != student_a.courses[session_a] and student_a != student_b:
                self.swap(student_a, session_a, student_b, session_b)
            if self.heuristic() >= current_happiness:
                current_happiness = self.happiness
                if step % 20 == 0:
                    self.points.append(current_happiness)
                    step = 0

                step += 1
            else:
                self.swap(student_a, session_a, student_b, session_b)
        print(self.count_0s())
        print(starting_happiness, current_happiness)
        self.print_equality()
        self.print_total()
        self.plot_histo()
        plt.plot(self.points)
        plt.ylabel('Happiness')
        plt.show()



LSS = LocalSearchSolver()
LSS.construct_from_file()
LSS.greedy_assign()
LSS.local_search()
