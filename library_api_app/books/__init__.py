from flask import Blueprint

books_bp = Blueprint('books', __name__)

from library_api_app.books import books