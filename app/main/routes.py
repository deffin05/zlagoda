import sqlite3

from flask_login import login_required

from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request

from app.main.forms import CategoryForm


@main_bp.route("/categories")
@login_required
def list_categories():
    db = get_db()
    cursor = db.cursor()
    categories = cursor.execute("SELECT * FROM Category ORDER BY category_name").fetchall()

    return render_template("categories/list.html", categories=categories)


@main_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryForm()

    if form.validate_on_submit():
        category_name = form["name"].data

        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute('INSERT INTO Category (category_number, category_name) VALUES (NULL, ?)', (category_name,))
            db.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('main.list_categories'))
        except sqlite3.Error as e:
            flash(f'Database error: {str(e)}', 'error')

    return render_template('categories/add.html', form=form)

@main_bp.route('/categories/edit/<int:category_number>', methods=['GET', 'POST'])
@login_required
def edit_category(category_number):
    db = get_db()
    cursor = db.cursor()

    category = cursor.execute("SELECT * FROM Category WHERE category_number = ?", (category_number,)).fetchone()

    form = CategoryForm(name=category["category_name"])

    if request.method == "POST" and form.validate_on_submit():
        category_name = form["name"].data

        try:
            cursor.execute('UPDATE Category SET category_name = ? WHERE category_number = ?', (category_name, category_number))
            db.commit()
            flash('Category added successfully!', 'success')
            return redirect(url_for('main.list_categories'))
        except sqlite3.Error as e:
            flash(f'Database error: {str(e)}', 'error')


    return render_template('categories/edit.html', form=form, category=category)

@main_bp.route('/categories/delete/<int:category_number>', methods=['POST'])
@login_required
def delete_category(category_number):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM Category WHERE category_number = ?', (category_number,))
        db.commit()
        flash('Category deleted successfully.', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Cannot delete category: {str(e)}', 'error')
    except sqlite3.Error as e:
        flash(f'Database error: {str(e)}', 'error')
    return redirect(url_for('main.list_categories'))