import sqlite3

from flask_login import login_required

from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request, abort


# from app.main.forms import ProductForm


@main_bp.route("/checks")
@login_required
def list_checks():
    db = get_db()
    cursor = db.cursor()
    checks = cursor.execute("""SELECT *
                               FROM "Check"
                               ORDER BY print_date DESC""").fetchall()

    return render_template("check/list.html", checks=checks)


@main_bp.route('/checks/delete/<check_number>', methods=['POST'])
@login_required
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
