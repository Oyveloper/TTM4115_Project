from class_manager.student.student_system import StudentSystem


def start_student():
    student_system = StudentSystem()
    student_system.run()

if __name__ == "__main__":
    start_student()