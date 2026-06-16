import sqlite3
from datetime import date, timedelta

from flask_login import login_required

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
                           selected_cashier_id=id_employee, start_date=start_date, end_date=end_date, today=date.today())


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
