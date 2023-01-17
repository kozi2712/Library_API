from flask import Blueprint

orders_bp = Blueprint('orders', __name__)

from library_api_app.orders import orders