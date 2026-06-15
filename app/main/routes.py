from flask import render_template
from flask_login import login_required

from app.main import main_bp


@main_bp.route("/stats")
@login_required
def stats():
    return render_template("stats/main.html")


@main_bp.route("/stats/cashiers")
@login_required
def cashier_stats():
    return render_template("stats/cashiers.html")


@main_bp.route("/stats/products")
@login_required
def product_stats():
    return render_template("stats/products.html")
