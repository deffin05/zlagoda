import sqlite3

from flask_login import login_required

from app.db import get_db
from app.main import main_bp

from flask import redirect, render_template, flash, url_for, request

from app.main.forms import StoreProductForm

def fetch_products(UPC: str, name: str, product_type: str):
    db = get_db()
    cursor = db.cursor()

    filters = []
    params = []
    query = """SELECT *, Product.product_name, Product.producer_name
                FROM Store_Product
                JOIN Product on Store_Product.id_product = Product.id_product
             """

    if UPC:
        filters.append("LOWER(UPC) LIKE LOWER(?)")
        params.append(f"%{UPC}%")
    if name:
        filters.append("LOWER(Product.product_name) LIKE LOWER(?)")
        params.append(f"%{name}%")
    if product_type == "1":
        filters.append("promotional_product = 1")
    elif product_type == "-1":
        filters.append("promotional_product = 0")

    if filters:
        query += ("WHERE " + " AND ".join(filters))

    query += " ORDER BY products_number DESC"

    products = cursor.execute(query, params).fetchall()

    return products


@main_bp.route("/store_products")
@login_required
def list_store_products():
    search_UPC = request.args.get("search_UPC", "")
    search_name = request.args.get("search_name", "")
    search_promo = request.args.get("search_promo", "")

    products = fetch_products(search_UPC, search_name, search_promo)

    return render_template("store_product/list.html", products=products)


@main_bp.route('/store_products/add', methods=['GET', 'POST'])
@login_required
def add_store_product():
    db = get_db()
    cursor = db.cursor()
    products = cursor.execute("SELECT id_product, product_name, producer_name FROM Product ORDER BY product_name")\
        .fetchall()

    product_choices = [(product["id_product"], product["product_name"] + " | " + product["producer_name"])
                       for product in products]

    upcs = cursor.execute("""SELECT Store_Product.UPC, Product.product_name, Product.producer_name
                                FROM Store_Product 
                                JOIN Product ON Store_Product.id_product = Product.id_product
                                ORDER BY Product.product_name""").fetchall()
    upc_choices = [("", "-- Оберіть товар --")] + \
                  [(upc["UPC"], upc["UPC"] + " | " + upc["product_name"] + " | " + upc["producer_name"]) for upc in upcs]

    form = StoreProductForm()
    form.id_product.choices = product_choices
    form.UPC_prom.choices = upc_choices

    if form.validate_on_submit():
        upc = form.UPC.data
        id_product = form.id_product.data
        selling_price = float(form.selling_price.data)
        products_number = form.products_number.data
        promotional_product = form.promotional_product.data
        upc_prom = form.UPC_prom.data

        try:
            if upc_prom:
                cursor.execute(
                    'INSERT INTO Store_Product '
                    '(UPC, id_product, selling_price, products_number, promotional_product, UPC_prom) '
                    'VALUES (?, ?, ?, ?, ?, ?)',
                    (upc, id_product, selling_price, products_number, promotional_product, upc_prom))
            else:
                cursor.execute(
                    'INSERT INTO Store_Product '
                    '(UPC, id_product, selling_price, products_number, promotional_product, UPC_prom) '
                    'VALUES (?, ?, ?, ?, ?, NULL)',
                    (upc, id_product, selling_price, products_number, promotional_product))

            db.commit()
            flash('Товар у магазині створено.', 'success')
            return redirect(url_for('main.list_store_products'))
        except sqlite3.Error as e:
            print(e)
            flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('store_product/add.html', form=form)


@main_bp.route('/store_products/edit/<upc>', methods=['GET', 'POST'])
@login_required
def edit_store_product(upc):
    db = get_db()
    cursor = db.cursor()

    store_product = cursor.execute("SELECT * FROM Store_Product WHERE UPC = ?", (upc,)).fetchone()
    if not store_product:
        flash("Товару в магазині з таким UPC не існує.", "error")
        return redirect(url_for('main.list_store_products'))

    products = cursor.execute("SELECT id_product, product_name, producer_name FROM Product ORDER BY product_name").fetchall()
    product_choices = [(product["id_product"], product["product_name"] + " | " + product["producer_name"])
                       for product in products]

    upcs = cursor.execute("""SELECT Store_Product.UPC, Product.product_name, Product.producer_name
                                FROM Store_Product 
                                JOIN Product ON Store_Product.id_product = Product.id_product
                                ORDER BY Product.product_name""").fetchall()
    upc_choices = [("", "-- Оберіть товар --")] + \
                  [(upc["UPC"], upc["UPC"] + " | " + upc["product_name"] + " | " + upc["producer_name"]) for upc in upcs]

    form = StoreProductForm(data=store_product)
    form.id_product.choices = product_choices
    form.UPC_prom.choices = upc_choices

    if request.method == "POST" and form.validate_on_submit():
        new_upc = form.UPC.data
        id_product = form.id_product.data
        selling_price = float(form.selling_price.data)
        products_number = form.products_number.data
        promotional_product = form.promotional_product.data
        upc_prom = form.UPC_prom.data

        try:
            if upc_prom:
                cursor.execute(
                    'UPDATE Store_Product '
                    'SET UPC = ?, id_product = ?, selling_price = ?, products_number = ?, '
                    'promotional_product = ?, UPC_prom = ?'
                    'WHERE UPC = ?',
                    (new_upc, id_product, selling_price, products_number, promotional_product, upc_prom, upc))
            else:
                cursor.execute(
                    'UPDATE Store_Product '
                    'SET UPC = ?, id_product = ?, selling_price = ?, products_number = ?, promotional_product = ?'
                    'WHERE UPC = ?',
                    (upc, id_product, selling_price, products_number, promotional_product, upc))

            db.commit()
            flash('Товар у магазині змінено', 'success')
            return redirect(url_for('main.list_store_products'))
        except sqlite3.Error as e:
            flash(f'Помилка бази даних: {str(e)}', 'error')

    return render_template('store_product/edit.html', form=form, product=store_product)


@main_bp.route('/store_products/delete/<upc>', methods=['POST'])
@login_required
def delete_store_product(upc):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM Store_Product WHERE UPC = ?', (upc,))
        db.commit()
        flash('Товар у магазині видалено.', 'success')
    except sqlite3.IntegrityError as e:
        flash(f'Неможливо видалити товар у магазині: {str(e)}', 'error')
    except sqlite3.Error as e:
        flash(f'Помилка бази даних: {str(e)}', 'error')
    return redirect(url_for('main.list_store_products'))
