from flask_login import login_required, current_user

from app.db import get_db
from app.main import main_bp

from flask import render_template


@main_bp.route("/profile")
@login_required
def display_profile():
    db = get_db()
    cursor = db.cursor()
    employee = cursor.execute("""SELECT * FROM Employee WHERE id_employee = ? LIMIT 1""", (current_user.id_employee,)).fetchone()

    return render_template("profile.html", employee=employee)
