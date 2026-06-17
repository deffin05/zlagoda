import sqlite3
from datetime import date, timedelta

from flask_login import login_required
from werkzeug.security import generate_password_hash

from app.auth.decorators import roles_required
from app.auth.forms import LoginForm
from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request

from app.main.forms import EmployeeForm


def fetch_cashiers():
    db = get_db()
    cursor = db.cursor()
    cashiers = cursor.execute("""SELECT id_employee, empl_surname, empl_name
                                 FROM Employee
                                 WHERE empl_role = 'Касир'
                                 ORDER BY empl_surname""").fetchall()

    return cashiers


@main_bp.route("/employees")
@login_required
@roles_required("manager")
def list_employees():
    db = get_db()
    cursor = db.cursor()
    search_surname = request.args.get("search_surname", "")
    search_role = request.args.get("search_role", "")
    employees = cursor.execute("""SELECT *
                                  FROM Employee
                                  WHERE lower(empl_surname) LIKE ? 
                                    AND empl_role LIKE ?
                                  ORDER BY empl_surname""",
                               (f"%{search_surname.lower()}%", f"{search_role}%")).fetchall()

    return render_template("employee/list.html", employees=employees)


@main_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@roles_required("manager")
def add_employee():
    form = EmployeeForm()

    if form.validate_on_submit():
        db = get_db()
        cursor = db.cursor()

        id_employee = form.id_employee.data
        empl_surname = form.empl_surname.data
        empl_name = form.empl_name.data
        empl_patronymic = form.empl_patronymic.data or None
        empl_role = form.empl_role.data
        salary = float(form.salary.data)
        date_of_birth = form.date_of_birth.data
        date_of_start = form.date_of_start.data
        phone_number = form.phone_number.data
        city = form.city.data
        street = form.street.data
        zip_code = form.zip_code.data

        if date_of_birth + timedelta(days=365) * 18 > date.today():
            flash('Співробітник не може бути молодшим за 18 років.', 'error')
        else:
            try:
                cursor.execute(
                    'INSERT INTO Employee '
                    '(id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth, '
                    'date_of_start, phone_number, city, street, zip_code) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth,
                     date_of_start, phone_number, city, street, zip_code)
                )

                db.commit()
                flash('Співробітника занесено', 'success')
                return redirect(url_for('main.list_employees'))
            except sqlite3.Error as e:
                print(e)
                flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('employee/add.html', form=form)


@main_bp.route('/employees/edit/<id_employee>', methods=['GET', 'POST'])
@login_required
@roles_required("manager")
def edit_employee(id_employee):
    db = get_db()
    cursor = db.cursor()

    employee = cursor.execute("SELECT * FROM Employee WHERE id_employee = ?", (id_employee,)).fetchone()
    if not employee:
        flash("Співробітника з таким ID не існує.", "error")
        return redirect(url_for('main.list_employees'))

    form = EmployeeForm(data=employee)

    if request.method == "POST" and form.validate_on_submit():
        new_id_employee = form.id_employee.data
        empl_surname = form.empl_surname.data
        empl_name = form.empl_name.data
        empl_patronymic = form.empl_patronymic.data or None
        empl_role = form.empl_role.data
        salary = float(form.salary.data)
        date_of_birth = form.date_of_birth.data
        date_of_start = form.date_of_start.data
        phone_number = form.phone_number.data
        city = form.city.data
        street = form.street.data
        zip_code = form.zip_code.data

        if date_of_birth + timedelta(days=365) * 18 > date.today():
            flash('Співробітник не може бути молодшим за 18 років.', 'error')
        else:
            try:
                cursor.execute(
                    'UPDATE Employee '
                    'SET id_employee = ?, empl_surname = ?, empl_name = ?, empl_patronymic = ?, empl_role = ?, salary = ?,'
                    'date_of_birth = ?, date_of_start = ?, phone_number = ?, city = ?, street = ?, zip_code = ?'
                    'WHERE id_employee = ?',
                    (new_id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth,
                     date_of_start, phone_number, city, street, zip_code, id_employee))
                db.commit()
                flash('Дані про співробітника змінено', 'success')
                return redirect(url_for('main.list_employees'))
            except sqlite3.Error as e:
                flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('employee/edit.html', form=form, employee=employee)


@main_bp.route('/employees/delete/<id_employee>', methods=['POST'])
@login_required
@roles_required("manager")
def delete_employee(id_employee):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM Employee WHERE id_employee = ?', (id_employee,))
        db.commit()
        flash('Співробітника видалено.', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Неможливо видалити співробітника: {str(e)}', 'error')
    except sqlite3.Error as e:
        flash(f'Помилка бази даних: {str(e)}', 'error')
    return redirect(url_for('main.list_employees'))


@main_bp.route('/employees/<id_employee>/create_user', methods=['GET','POST'])
@login_required
@roles_required("manager")
def create_user(id_employee):
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""INSERT INTO User (id_employee, email, password)
                          VALUES (?, ?, ?)""", (id_employee, email, generate_password_hash(password)))

        db.commit()
        flash("Аккаунт створено", "success")
        return redirect(url_for('main.list_employees'))
    return render_template('employee/create_user.html', form=form)