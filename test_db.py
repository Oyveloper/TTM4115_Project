from class_manager.class_manager.db import Database, Question


if __name__ == "__main__":
    d = Database()

    d.remove_all_questions()
    d.add_question(Question("What is a state machine?", "A diagram that shows the states of a system and the transitions between them."))
    d.add_question(Question("What is a state?", "A state is a condition that a system can be in."))
    d.add_question(Question("What is a transition?", "A transition is a change from one state to another."))

    d.get_question(0)
    print(d.nbr_questions())