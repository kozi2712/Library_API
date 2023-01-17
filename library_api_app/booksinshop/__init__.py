from flask import Blueprint

booksinshop_bp = Blueprint('booksinshop', __name__)

from library_api_app.booksinshop import booksinshop