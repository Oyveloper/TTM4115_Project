import logging

from class_manager.instructor.instructor_system import InstructorSystem
from class_manager.student.student_system import StudentSystem

def main():
    print("hello world")
    debug_level = logging.DEBUG
    logger = logging.getLogger(__name__)
    logger.setLevel(debug_level)
    ch = logging.StreamHandler()
    ch.setLevel(debug_level)
    formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    instructor_system = InstructorSystem()
    student_system = StudentSystem()
    student_system.run()
    #instructor_system.run()

if __name__ == "__main__":
    main()