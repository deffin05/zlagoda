from datetime import date, timedelta

from flask import render_template, request
from flask_login import login_required

from app.db import get_db
from app.main import main_bp
from app.main.employee import fetch_cashiers


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

    cashiers = fetch_cashiers()

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
        period = "all"

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
                           start_date=start_date, end_date=end_date, today=date.today(), cashiers=cashiers,
                           sum=total_sum)


@main_bp.route("/stats/products")
@login_required
def product_stats():
    id_product = request.args.get("id_product")
    period = request.args.get("period")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    db = get_db()
    cursor = db.cursor()

    products = cursor.execute("SELECT id_product, product_name FROM Product ORDER BY product_name").fetchall()

    sub_query = """SELECT P.id_product, P.product_name, P.producer_name, SUM(S.product_number) as product_amount
                   FROM Sale S
                            JOIN Store_Product SP ON S.UPC = SP.UPC
                            JOIN Product P ON SP.id_product = P.id_product
                            JOIN "Check" C ON S.check_number = C.check_number """
    filters = []
    params = []

    if id_product:
        filters.append("P.id_product = ?")
        params.append(id_product)

    if period in ["today", "yesterday", "7", "30", "year", "custom"]:
        filters.append("DATE(C.print_date) BETWEEN ? AND ?")
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
        period = "all"

    if filters:
        sub_query += " WHERE " + " AND ".join(filters)

    sub_query += " GROUP BY P.id_product, P.product_name, P.producer_name"

    rows = cursor.execute(sub_query, params).fetchall()

    total_sum = 0
    for row in rows:
        total_sum += row["product_amount"]
        
    return render_template("stats/products.html", rows=rows, products=products,
                           selected_product_id=id_product, period=period,
                           start_date=start_date, end_date=end_date, today=date.today(), sum=total_sum)


@main_bp.route("/stats/top_5_products")
@login_required
def top_5_products():
    # Запит
    query = """SELECT P.id_product, P.product_name, SUM(Sale.selling_price * Sale.product_number) total_sum
               FROM Sale
                        JOIN Store_Product SP ON Sale.UPC = SP.UPC
                        JOIN Product P ON SP.id_product = P.id_product
                        JOIN "Check" C ON C.check_number = Sale.check_number
               WHERE C.card_number IS NOT NULL
               GROUP BY P.id_product
               ORDER BY total_sum DESC
               LIMIT 5"""

    db = get_db()  # Отримання з'єднання з базою даних
    cursor = db.cursor()

    rows = cursor.execute(query).fetchall()  # Надсилання запиту

    # Надсилання результатів на інтерфейс користувача
    return render_template("stats/top_5_products.html", rows=rows)


@main_bp.route("/stats/popular_among_customers")
@login_required
def popular_among_customers():
    percent = request.args.get("percent", -1)

    query = """SELECT P.id_product, P.product_name
               FROM Product P
               WHERE EXISTS(SELECT 1
                            FROM Customer_Card
                            WHERE percent = ?)
                 AND NOT EXISTS (SELECT CC.card_number
                                 FROM Customer_Card CC
                                 WHERE CC.percent = ?
                                   AND NOT EXISTS (SELECT Sale.UPC
                                                   FROM Sale
                                                            JOIN "Check" C ON Sale.check_number = C.check_number
                                                            JOIN Store_Product SP ON Sale.UPC = SP.UPC
                                                   WHERE C.card_number = CC.card_number
                                                     AND SP.id_product = P.id_product));
            """
    
    rows = cursor.execute(query, (percent, percent)).fetchall()

    return render_template("stats/popular_among_customers.html", rows=rows)


@main_bp.route("/stats/client_promo")
@login_required
def client_promo_stats():
    # Отримання параметрів запиту
    period = request.args.get("period")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Підключення до бази даних
    db = get_db()
    cursor = db.cursor()

    # Підготовка підзапиту
    sub_query = """SELECT CC.card_number, CC.cust_surname, CC.cust_name, CC.cust_patronymic,
                      CC.percent, COUNT(DISTINCT C.check_number) AS purchase_number
               FROM Customer_Card CC
               JOIN "Check" C ON CC.card_number = C.card_number
               WHERE C.check_number IN (SELECT S.check_number
                                    FROM Sale S
                                    WHERE S.UPC IN (SELECT SP.UPC
                                                FROM Store_Product SP
                                                WHERE SP.promotional_product = 1))"""
    filters = []
    params = []
    
    # Обробка періоду для фільтрації даних
    if period in ["today", "yesterday", "7", "30", "year", "custom"]:
        filters.append("DATE(C.print_date) BETWEEN ? AND ?")
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
        period = "all"

    # Додавання фільтрів до підзапиту, якщо вони існують
    if filters:
        sub_query += " AND " + " AND ".join(filters)

    # Групування результатів за номером картки клієнта
    sub_query += " GROUP BY CC.card_number"

    # Виконання підзапиту та отримання результатів
    rows = cursor.execute(sub_query, params).fetchall()

    # Повернення результатів у шаблон для відображення
    return render_template("stats/client_promo.html", rows=rows, period=period,
                         start_date=start_date, end_date=end_date, today=date.today())

@main_bp.route("/stats/client_categories")
@login_required
def client_categories_stats():
    period = request.args.get("period")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    db = get_db()
    cursor = db.cursor()

    sub_query = """SELECT CC.card_number, CC.cust_surname, CC.cust_name, CC.cust_patronymic,
                      CC.percent
               FROM Customer_Card CC
               JOIN "Check" C ON CC.card_number = C.card_number
               WHERE NOT EXISTS (SELECT 1
                                FROM Category Ca
                                WHERE NOT EXISTS (SELECT 1
                                                FROM "Check" C2
                                                JOIN Sale S ON C2.check_number = S.check_number
                                                JOIN Store_Product SP ON S.UPC = SP.UPC
                                                JOIN Product P ON SP.id_product = P.id_product
                                                WHERE C2.card_number = CC.card_number
                                                AND P.category_number = Ca.category_number))"""
    filters = []
    params = []
    
    if period in ["today", "yesterday", "7", "30", "year", "custom"]:
        filters.append("DATE(C.print_date) BETWEEN ? AND ?")
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
        period = "all"

    if filters:
        sub_query += " AND " + " AND ".join(filters)

    sub_query += " GROUP BY CC.card_number"

    rows = cursor.execute(sub_query, params).fetchall()

    return render_template("stats/client_categories.html", rows=rows, period=period,
                         start_date=start_date, end_date=end_date, today=date.today())
