from flask import Blueprint

main_bp = Blueprint('main', __name__)

from app.main import category, product, store_product, employee, customer, check, profile
