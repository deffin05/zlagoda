from flask import render_template, request
from flask_login import login_required

from app.db import get_db
from app.main import main_bp


@main_bp.route("/stats")
@login_required
def stats():
    return render_template("stats/main.html")


@main_bp.route("/stats/cashiers")
@login_required
def cashier_stats():
    id_employee = request.args.get("id_employee")
    period = request.args.get("period")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    db = get_db()
    cursor = db.cursor()

    query = """SELECT id_employee, SUM(sum_total) cahier_sum FROM "Check" GROUP BY id_employee"""

    rows = cursor.execute(query).fetchall()

    return render_template("stats/cashiers.html", rows=rows, id_employee=id_employee, period=period,
                           start_date=start_date, end_date=end_date)


@main_bp.route("/stats/products")
@login_required
def product_stats():
    return render_template("stats/products.html")
