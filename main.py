import click
import threading
from class_manager.class_manager.class_manager_system import ClassManagerSystem

from class_manager.instructor.instructor_system import InstructorSystem
from class_manager.student.student_system import StudentSystem


def start_student():
    student_system = StudentSystem()
    student_system.run()


def start_instructor():
    instructor_system = InstructorSystem()
    instructor_system.run()


def start_server():
    c_syst = ClassManagerSystem()
    c_syst.run()


@click.group()
def cli():
    pass


@cli.command()
def student():
    start_student()


@cli.command()
def instructor():
    start_instructor()


@cli.command()
def server():
    start_server()


@cli.command()
def all():
    threading.Thread(target=start_server).start()
    threading.Thread(target=start_student).start()
    threading.Thread(target=start_instructor).start()


if __name__ == "__main__":
    cli()
