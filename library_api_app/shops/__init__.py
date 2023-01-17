from flask import Blueprint

shops_bp = Blueprint('shops', __name__)

from library_api_app.shops import shops