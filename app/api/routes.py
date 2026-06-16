from flask_login import login_required

from app.api import api_bp
from app.db import get_db

from flask import request, jsonify


@api_bp.route("/customers", methods=["GET"])
@login_required
def api_customers():
    query = request.args.get("q", "")

    db = get_db()
    cursor = db.cursor()

    sql = """SELECT card_number, cust_surname, cust_name, cust_patronymic, percent
             FROM Customer_Card
             WHERE LOWER(card_number) LIKE ? OR LOWER(cust_surname) LIKE ?
             ORDER BY cust_surname"""

    rows = cursor.execute(sql, (f"%{query.lower()}%", f"%{query.lower()}%")).fetchall()

    result = [{
        "number": r["card_number"],
        "name": f"{r["cust_surname"]} {r["cust_name"]} {(r["cust_patronymic"] or "")}".strip(),
        "percent": r["percent"],
    } for r in rows]

    return jsonify(result), 200