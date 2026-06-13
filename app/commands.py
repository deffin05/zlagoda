import sqlite3
import click
from werkzeug.security import generate_password_hash
from app.db import get_db


@click.command('create-user')
@click.option('--id-employee', prompt='Employee ID', default="0000000000", help='The unique employee ID.')
@click.option('--email', prompt='Email Address', default="root@zlagoda.com", help='The email address for the user.')
@click.option('--password', prompt=True, hide_input=True, default="root", confirmation_prompt=True, help='The password.')
def create_user(id_employee, email, password):
    """Register a manager user in the database."""
    db = get_db()
    cursor = db.cursor()

    hashed_password = generate_password_hash(password)

    try:
        cursor.execute(
            """INSERT INTO Employee (id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary,
                                     date_of_birth, date_of_start, phone_number, city, street, zip_code)
               VALUES (?, 'Петро', 'Іваненко', 'Васильович', 'Менеджер', 20000, '1990-01-01', '2020-01-01', '+380000000000',
                       'Київ', 'просп. Степана Бандери 1', '04101')""",
            (id_employee, )
        )
        cursor.execute(
            "INSERT INTO User (id_employee, email, password) VALUES (?, ?, ?)",
            (id_employee, email, hashed_password)
        )

        db.commit()
        click.echo(f"Successfully registered user: {email}")
    except sqlite3.IntegrityError as e:
        db.rollback()
        click.echo(f"Registration failed: {e}", err=True)
    except Exception as e:
        db.rollback()
        click.echo(f"An unexpected error occurred: {e}", err=True)
