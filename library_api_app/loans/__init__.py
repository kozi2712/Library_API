from flask import Blueprint

loans_bp = Blueprint('loans', __name__)

from library_api_app.loans import loans