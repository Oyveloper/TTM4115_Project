from class_manager.class_manager.class_manager_system import ClassManagerSystem


def start_server():
    c_syst = ClassManagerSystem()
    c_syst.run()

if __name__ == "__main__":
    start_server()