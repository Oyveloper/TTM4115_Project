from stmpy import Driver
from class_manager.instructor.instructor_ui import InstructorUISTM


class InstructorSystem:
    def run(self):

        ui = InstructorUISTM()

        self.driver = Driver()
        self.driver.add_machine(ui.stm)
        self.driver.start()

        ui.create_gui()
