import sqlite3
class Question:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer


class Database:
    def __init__(self):
        self.db: sqlite3.Connection = sqlite3.connect('questions.db')

        self.db.execute("CREATE TABLE IF NOT EXISTS questions (question TEXT, answer TEXT)")

    def add_question(self, question: Question):
        self.db.execute("INSERT INTO questions (question, answer) VALUES (?, ?)", (question.question, question.answer))
        self.db.commit()

    def remove_all_questions(self):
        self.db.execute("DELETE FROM questions")

    def nbr_questions(self):
        res = self.db.execute("SELECT COUNT(*) FROM questions")
        count = res.fetchall()
        return count[0][0]


    def get_question(self, index: int) -> Question:
        res = self.db.execute("SELECT * FROM questions")
        all = res.fetchall()
        print(all)

        return all[index]