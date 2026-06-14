import sqlite3

from flask_login import login_required

from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request, abort

from app.main.forms import ProductForm


@main_bp.route("/products")
@login_required
def list_products():
    db = get_db()
    cursor = db.cursor()
    products = cursor.execute("""SELECT Product.*, Category.category_name 
                                    FROM Product 
                                    JOIN Category ON Product.category_number = Category.category_number
                                    ORDER BY Product.product_name""").fetchall()

    return render_template("product/list.html", products=products)


@main_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    db = get_db()
    cursor = db.cursor()
    categories = cursor.execute("SELECT * FROM Category ORDER BY category_name").fetchall()
    category_choices = [(cat["category_number"], cat["category_name"]) for cat in categories]

    form = ProductForm()
    form.category_number.choices = category_choices


    if form.validate_on_submit():
        id_product = form.id_product.data
        category_number = form.category_number.data
        producer_name = form.producer_name.data
        product_name = form.product_name.data
        characteristics = form.characteristics.data

        try:
            if id_product:
                cursor.execute(
                    'INSERT INTO Product (id_product, category_number, product_name, producer_name, characteristics) '
                    'VALUES (?, ?, ?, ?, ?)', (id_product, category_number, product_name, producer_name, characteristics))
            else:
                cursor.execute('INSERT INTO Product (id_product, category_number, product_name, producer_name, characteristics) '
                               'VALUES (NULL, ?, ?, ?, ?)', (category_number, product_name, producer_name, characteristics))

            db.commit()
            flash('Продукт створено', 'success')
            return redirect(url_for('main.list_products'))
        except sqlite3.Error as e:
            flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('product/add.html', form=form)

@main_bp.route('/products/edit/<int:id_product>', methods=['GET', 'POST'])
@login_required
def edit_product(id_product):
    db = get_db()
    cursor = db.cursor()

    product = cursor.execute("SELECT * FROM Product WHERE id_product = ?", (id_product,)).fetchone()
    if not product:
        flash("Продукту з таким ID не існує.", "error")
        return redirect(url_for('main.list_products'))

    form = ProductForm(data=product)

    categories = cursor.execute("SELECT * FROM Category").fetchall()
    category_choices = [(cat["category_number"], cat["category_name"]) for cat in categories]
    form.category_number.choices = category_choices

    if request.method == "POST" and form.validate_on_submit():
        new_id_product = form.id_product.data
        category_number = form.category_number.data
        product_name = form.product_name.data
        producer_name = form.producer_name.data
        characteristics = form.characteristics.data

        try:
            cursor.execute(
                'UPDATE Product '
                'SET id_product = ?, product_name = ?, category_number = ?, characteristics = ?, producer_name = ?'
                'WHERE id_product = ?',
                (new_id_product, product_name, category_number, characteristics, producer_name, id_product))
            db.commit()
            flash('Продукт змінено', 'success')
            return redirect(url_for('main.list_products'))
        except sqlite3.Error as e:
            flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('product/edit.html', form=form, product=product)

@main_bp.route('/products/delete/<int:id_product>', methods=['POST'])
@login_required
def delete_product(id_product):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM Product WHERE id_product = ?', (id_product,))
        db.commit()
        flash('Продукт видалено.', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Неможливо видалити продукт: {str(e)}', 'error')
    except sqlite3.Error as e:
        flash(f'Помилка бази даних: {str(e)}', 'error')
    return redirect(url_for('main.list_products'))