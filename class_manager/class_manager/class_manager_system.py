import logging
from stmpy import Driver
from class_manager.class_manager.class_manager import ClassManagerSTM
from class_manager.instructor.instructor_ui import InstructorUISTM


class ClassManagerSystem:
    def run(self):
        class_manager = ClassManagerSTM()
