import sqlite3
from datetime import date, timedelta

from flask_login import login_required

from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request

from app.main.forms import EmployeeForm


@main_bp.route("/employees")
@login_required
def list_employees():
    db = get_db()
    cursor = db.cursor()
    employees = cursor.execute("""SELECT *  FROM Employee ORDER BY empl_surname""").fetchall()

    return render_template("employee/list.html", employees=employees)


@main_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    form = EmployeeForm()

    if form.validate_on_submit():
        db = get_db()
        cursor = db.cursor()

        id_employee = form.id_employee.data
        empl_surname = form.empl_surname.data
        empl_name = form.empl_surname.data
        empl_patronymic = form.empl_surname.data or None
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
def edit_employee(id_employee):
    db = get_db()
    cursor = db.cursor()

    employee = cursor.execute("SELECT * FROM Employee WHERE id_employee = ?", (id_employee,)).fetchone()
    if not employee:
        flash("Співробітника з таким ID не існує.", "error")
        return redirect(url_for('main.list_employees'))

    form = EmployeeForm(data=employee)

    if request.method == "POST" and form.validate_on_submit():
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
                    'UPDATE Employee '
                    'SET id_employee = ?, empl_surname = ?, empl_name = ?, empl_patronymic = ?, empl_role = ?, salary = ?,'
                    'date_of_birth = ?, date_of_start = ?, phone_number = ?, city = ?, street = ?, zip_code = ?'
                    'WHERE id_employee = ?',
                    (id_employee, empl_surname, empl_name, empl_patronymic, empl_role, salary, date_of_birth,
                     date_of_start, phone_number, city, street, zip_code, id_employee))
                db.commit()
                flash('Дані про співробітника змінено', 'success')
                return redirect(url_for('main.list_employees'))
            except sqlite3.Error as e:
                flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('employee/edit.html', form=form, employee=employee)


@main_bp.route('/employees/delete/<id_employee>', methods=['POST'])
@login_required
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
