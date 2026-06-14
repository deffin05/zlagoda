from typing import override

from flask_login import UserMixin

from app.db import get_db


class User(UserMixin):
    def __init__(self, id_employee, email, password, role):
        self.id_employee = id_employee
        self.email = email
        self.password = password
        self.role = role

    @override
    def get_id(self):
        return self.id_employee

    @classmethod
    def get_by_id(cls, id_employee):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT User.id_employee, User.email, User.password, Employee.empl_role "
                       "FROM User "
                       "JOIN Employee ON Employee.id_employee = User.id_employee "
                       "WHERE User.id_employee = ?", (id_employee,))
        row = cursor.fetchone()
        role = "manager" if row["empl_role"] == "Менеджер" else "cashier"
        if row:
            return cls(row["id_employee"], row["email"], row["password"], role)
        return None

    @classmethod
    def get_by_email(cls, email):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT User.id_employee, User.email, User.password, Employee.empl_role "
                       "FROM User "
                       "JOIN Employee ON Employee.id_employee = User.id_employee "
                       "WHERE email = ?", (email,))

        row = cursor.fetchone()
        role = "manager" if row["empl_role"] == "Менеджер" else "cashier"
        if row:
            return cls(row["id_employee"], row["email"], row["password"], role)
        return None
