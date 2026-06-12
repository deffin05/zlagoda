from flask_login import UserMixin

from app.db import get_db


class User(UserMixin):
    def __init__(self, id_employee, email, password):
        self.id_employee = id_employee
        self.email = email
        self.password = password

    def get_by_id(self, id_employee):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id_employee, email, password FROM users WHERE id_employee = ?", (id_employee,))

        row = cursor.fetchone()
        if row:
            return User(row["id_employee"], row["email"], row["password"])
        return None

    def get_by_email(self, email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id_employee, email, password FROM users WHERE email = ?", (email,))

        row = cursor.fetchone()
        if row:
            return User(row["id_employee"], row["email"], row["password"])
        return None
