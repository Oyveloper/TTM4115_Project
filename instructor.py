

from class_manager.instructor.instructor_system import InstructorSystem


def start_instructor():
    instructor_system = InstructorSystem()
    instructor_system.run()

if __name__ == "__main__":
    start_instructor()