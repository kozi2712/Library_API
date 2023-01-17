from flask import Blueprint

publish_house_bp = Blueprint('publishing_house', __name__)

from library_api_app.publishing_house import publishing_house