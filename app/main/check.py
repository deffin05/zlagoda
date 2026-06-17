import random
import sqlite3
import string
from datetime import date, timedelta, datetime
from flask_login import login_required, current_user

from app.auth.decorators import roles_required
from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request, abort

from app.main.employee import fetch_cashiers


def fetch_checks(id_employee, period, start_date, end_date):
    db = get_db()
    cursor = db.cursor()

    query = """SELECT "Check".*, Employee.empl_surname, Employee.empl_name, Employee.empl_patronymic
               FROM "Check"
                        JOIN Employee ON Employee.id_employee = "Check".id_employee"""
    filters = []
    params = []

    if id_employee:
        filters.append('"Check".id_employee = ?')
        params.append(id_employee)

    if period in ["today", "yesterday", "7", "30", "year", "custom"]:
        filters.append("DATE(print_date) BETWEEN ? AND ?")
        today = date.today()
        match period:
            case "today":
                start_date = today
                end_date = today
            case "yesterday":
                yesterday = today - timedelta(days=1)
                start_date = yesterday
                end_date = yesterday
            case "7":
                start_date = today - timedelta(days=6)
                end_date = today
            case "30":
                start_date = today - timedelta(days=29)
                end_date = today
            case "year":
                start_date = today - timedelta(days=365)
                end_date = today
        params.append(start_date)
        params.append(end_date)

    if filters:
        query += " WHERE " + " AND ".join(filters)

    query += " ORDER BY print_date DESC"

    return cursor.execute(query, params).fetchall()


@main_bp.route("/checks")
@login_required
def list_checks():
    id_employee = request.args.get("search_employee")
    period = request.args.get("search_period")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    checks = fetch_checks(id_employee, period, start_date, end_date)

    if period not in ["today", "yesterday", "7", "30", "year", "custom"]:
        period = "all"

    return render_template("check/list.html", checks=checks, cashiers=fetch_cashiers(), selected_period=period,
                           selected_cashier_id=id_employee, start_date=start_date, end_date=end_date,
                           today=date.today())


@main_bp.route("/checks/create", methods=["GET", "POST"])
@login_required
def check_create():
    if request.method == "POST":
        card_number = request.form.get("card_number", "")
        upcs = request.form.getlist("upc[]")
        quantities = request.form.getlist("quantity[]")

        if len(upcs) != len(quantities) or len(upcs) == 0:
            flash("Оберіть товари.", "error")
            return render_template("check/create.html")

        db = get_db()
        cursor = db.cursor()

        card_number_fetched = None
        discount = 0
        if card_number:
            card = cursor.execute("SELECT card_number, percent FROM Customer_Card WHERE card_number = ?",
                                  (card_number,)).fetchone()
            if card:
                card_number_fetched = card["card_number"]
                discount = card["percent"]

        employee = current_user.id_employee
        try:
            cursor.execute("BEGIN IMMEDIATE;")
            total_price = 0
            prices = []
            for i in range(len(upcs)):
                upc = upcs[i]
                product = cursor.execute("""SELECT selling_price
                                            FROM Store_Product
                                            WHERE UPC = ?""", (upc,)).fetchone()

                cursor.execute("""UPDATE Store_Product
                                  SET products_number = (products_number - ?)
                                  WHERE UPC = ?""", (quantities[i], upc))

                total_price += float(product["selling_price"]) * int(quantities[i])
                prices.append(product["selling_price"])

            while True:
                check_number = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
                check = cursor.execute("""SELECT check_number
                                          FROM "Check"
                                          WHERE check_number = ?""", (check_number,)).fetchone()
                if not check:
                    break

            discount_frac = 1 - (discount / 100)
            total_price *= discount_frac

            cursor.execute("""INSERT INTO "Check" (check_number, id_employee, card_number, print_date, sum_total, vat)
                              VALUES (?, ?, ?, ?, ?, ?)""",
                           (check_number, employee, card_number_fetched, datetime.now(), total_price,
                            total_price * 0.2))

            for i in range(len(upcs)):
                cursor.execute("""INSERT INTO Sale (UPC, check_number, product_number, selling_price)
                                  VALUES (?, ?, ?, ?)""", (upcs[i], check_number, quantities[i], prices[i]))

            db.commit()
        except Exception as e:
            print(e)
            db.rollback()
            flash(f"Помилка бази даних: {e}", "error")
            return render_template("check/create.html")

    return render_template("check/create.html")


@main_bp.route('/checks/delete/<check_number>', methods=['POST'])
@login_required
@roles_required("manager")
def delete_check(check_number):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM "Check" WHERE check_number = ?', (check_number,))
        db.commit()
        flash('Чек видалено.', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Неможливо видалити чек: {str(e)}', 'error')
    except sqlite3.Error as e:
        flash(f'Помилка бази даних: {str(e)}', 'error')
    return redirect(url_for('main.list_products'))
