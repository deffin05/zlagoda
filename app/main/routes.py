from datetime import date, timedelta

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

    cashiers = cursor.execute("""SELECT id_employee, empl_surname, empl_name
                                 FROM Employee
                                 WHERE empl_role = 'Касир'
                                 ORDER BY empl_surname""").fetchall()

    sub_query = """SELECT id_employee, SUM(sum_total) cashier_sum
               FROM "Check" """
    filters = []
    params = []

    if id_employee:
        filters.append("id_employee = ?")
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
    else:
        period="all"

    if filters:
        sub_query += " WHERE " + " AND ".join(filters)

    sub_query += " GROUP BY id_employee"

    main_query = f"""SELECT E.id_employee, empl_surname, empl_name, empl_patronymic, cashier_sum
                    FROM Employee E
                    JOIN ({sub_query}) C ON E.id_employee = C.id_employee"""

    rows = cursor.execute(main_query, params).fetchall()

    total_sum = 0
    for row in rows:
        total_sum += row["cashier_sum"]

    return render_template("stats/cashiers.html", rows=rows, selected_cashier_id=id_employee, period=period,
                           start_date=start_date, end_date=end_date, today=date.today(), cashiers=cashiers, sum=total_sum)


@main_bp.route("/stats/products")
@login_required
def product_stats():
    return render_template("stats/products.html")
