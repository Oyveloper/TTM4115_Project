import logging

from class_manager.instructor.instructor_system import InstructorSystem

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
    instructor_system.run()

if __name__ == "__main__":
    main()