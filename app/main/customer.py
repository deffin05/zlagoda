import sqlite3
from datetime import date, timedelta

from flask_login import login_required

from app.auth.decorators import roles_required
from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request

from app.main.forms import CustomerForm


def fetch_customers(surname: str, percent: str):
    db = get_db()
    cursor = db.cursor()

    filters = []
    params = []
    querry = """SELECT *
                FROM Customer_Card
             """

    if surname:
        filters.append("LOWER(cust_surname) LIKE LOWER(?)")
        params.append(f"%{surname}%")

    if percent.isdigit():
        filters.append("percent = ?")
        params.append(int(percent))

    if filters:
        querry += ("WHERE " + " AND ".join(filters))

    querry += " ORDER BY cust_surname"

    customers = cursor.execute(querry, params).fetchall()

    return customers


@main_bp.route("/customers")
@login_required
def list_customers():
    search_surname = request.args.get("search_surname", "").strip()
    search_percent = request.args.get("search_percent", "").strip()

    customers = fetch_customers(search_surname, search_percent)

    return render_template("customer/list.html", customers=customers)


@main_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()

    if form.validate_on_submit():
        db = get_db()
        cursor = db.cursor()

        card_number = form.card_number.data
        cust_surname = form.cust_surname.data
        cust_name = form.cust_name.data
        cust_patronymic = form.cust_patronymic.data or None
        phone_number = form.phone_number.data
        city = form.city.data or None
        street = form.street.data or None
        zip_code = form.zip_code.data or None
        percent = form.percent.data

        try:
            cursor.execute(
                'INSERT INTO Customer_Card '
                '(card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent)
            )

            db.commit()
            flash('Карту клієнта створено', 'success')
            return redirect(url_for('main.list_customers'))
        except sqlite3.Error as e:
            flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('customer/add.html', form=form)


@main_bp.route('/customers/edit/<card_number>', methods=['GET', 'POST'])
@login_required
def edit_customer(card_number):
    db = get_db()
    cursor = db.cursor()

    customer = cursor.execute("SELECT * FROM Customer_Card WHERE card_number = ?", (card_number,)).fetchone()
    if not customer:
        flash("Карти клієнта з таким номером не існує..", "error")
        return redirect(url_for('main.list_customers'))

    form = CustomerForm(data=customer)

    if request.method == "POST" and form.validate_on_submit():
        new_card_number = form.card_number.data
        cust_surname = form.cust_surname.data
        cust_name = form.cust_name.data
        cust_patronymic = form.cust_patronymic.data or None
        phone_number = form.phone_number.data
        city = form.city.data or None
        street = form.street.data or None
        zip_code = form.zip_code.data or None
        percent = form.percent.data

        try:
            cursor.execute(
                'UPDATE Customer_Card '
                'SET card_number = ?, cust_surname = ?, cust_name = ?, cust_patronymic = ?, phone_number = ?, city = ?, '
                'street = ?, zip_code = ?, percent = ?'
                'WHERE card_number = ?',
                (new_card_number, cust_surname, cust_name, cust_patronymic, phone_number, city, street, zip_code, percent,
                 card_number))
            db.commit()
            flash('Дані про карту клієнта змінено', 'success')
            return redirect(url_for('main.list_customers'))
        except sqlite3.Error as e:
            flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('customer/edit.html', form=form, customer=customer)


@main_bp.route('/customers/delete/<card_number>', methods=['POST'])
@login_required
@roles_required("manager")
def delete_customer(card_number):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM Customer_Card WHERE card_number = ?', (card_number,))
        db.commit()
        flash('Карту клієнта видалено.', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Неможливо видалити карту клієнта: {str(e)}', 'error')
    except sqlite3.Error as e:
        flash(f'Помилка бази даних: {str(e)}', 'error')
    return redirect(url_for('main.list_customers'))
