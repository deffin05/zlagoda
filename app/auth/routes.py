from flask_login import login_user
from werkzeug.security import check_password_hash

from app.models import User
from app.auth.forms import LoginForm
from app.auth import auth_bp

from flask import redirect, render_template, flash, url_for, request


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)

        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or "/")
        else:
            flash('Invalid login credentials.', 'danger')

    return render_template("auth.html", form=form)
