from stmpy import Driver
from class_manager.student.student_ui import StudentUISTM


class StudentSystem:
    def run(self):

        ui = StudentUISTM()

        self.driver = Driver()
        self.driver.add_machine(ui.stm)
        self.driver.start()

        ui.create_gui()
