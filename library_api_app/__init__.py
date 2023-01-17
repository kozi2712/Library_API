from flask import Flask, render_template, make_response
from flask_celeryext import FlaskCeleryExt
from flask_login import LoginManager
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from library_api_app.flask_celery import make_celery


db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
login_manager = LoginManager()
ext_celery = FlaskCeleryExt(create_celery_app=make_celery)


def create_app(config_class=Config):
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)
    app.config.from_object(config_class)
    app.config['CORS_HEADERS'] = 'Content-Type'
    ma.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ext_celery.init_app(app)
    login_manager.init_app(app)

    from library_api_app.commands import db_manage_bp
    from library_api_app.authors import authors_bp
    from library_api_app.errors import errors_bp
    from library_api_app.books import books_bp
    from library_api_app.auth import auth_bp
    from library_api_app.category import category_bp
    from library_api_app.publishing_house import publish_house_bp
    from library_api_app.loans import loans_bp
    from library_api_app.orders import orders_bp
    from library_api_app.shops import shops_bp
    from library_api_app.booksinshop import booksinshop_bp

    app.register_blueprint(db_manage_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(authors_bp, url_prefix='/api/v1')
    app.register_blueprint(books_bp, url_prefix='/api/v1')
    app.register_blueprint(loans_bp, url_prefix='/api/v1')
    app.register_blueprint(category_bp, url_prefix='/api/v1')
    app.register_blueprint(orders_bp, url_prefix='/api/v1')
    app.register_blueprint(publish_house_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(shops_bp, url_prefix='/api/v1')
    app.register_blueprint(booksinshop_bp, url_prefix='/api/v1')

    @app.route("/")
    def base():
        return render_template("base.html")

    return app
