import sqlite3
class Question:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


class Database:
    def __init__(self):
        self.db: sqlite3.Connection = sqlite3.connect('questions.db')

    def add_question(self, question: Question):
        self.db.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question.question, question.answer))
        self.db.commit()

    def get_question(self, index: int) -> Question:
        res = self.db.execute("SELECT * FROM questions WHERE id = ?", (index,))
        print(res.fetchone())