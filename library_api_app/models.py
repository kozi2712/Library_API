import json

import jwt

from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, ValidationError, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, EqualTo
from datetime import datetime, date, timedelta
from marshmallow import Schema, fields, validate, validates, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from library_api_app import db

class CustomEncoder(json.JSONEncoder):
    def default(
        self,
        o,
    ):
        """
        A custom default encoder.
        In reality this should work for nearly any iterable.
        """
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)


class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    books = db.relationship('Book', back_populates='author', cascade='all, delete-orphan')

    def __init__(self, fn, ln, bd):
        self.first_name = fn
        self.last_name = ln
        self.birth_date = bd


    def __repr__(self):
        return f'<{self.__class__.__name__}>: {self.first_name} {self.last_name}'

    @staticmethod
    def additional_validation(param: str, value: str) -> date:
        if param == 'birth_date':
            try:
                value = datetime.strptime(value, '%d-%m-%Y').date()
            except ValueError:
                value = None
        return value


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True, index=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    loans = db.relationship('Loans', back_populates='user')
    orders = db.relationship('Orders', back_populates='user')

    def __init__(self, un, em, pwd):
        self.username = un
        self.email = em
        self.password = pwd

    @staticmethod
    def generate_hashed_password(password: str) -> str:
        return generate_password_hash(password)

    def generate_jwt(self):
        payload = {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,
            'creation_date': self.creation_date.timestamp(),
            'exp': datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRED_MINUTES', 5))
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY'))

    def is_password_valid(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<Name %r>' % self.username


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    books = db.relationship('Book', back_populates='category', cascade='all, delete-orphan')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class PublishingHouse(db.Model):
    __tablename__ = 'publishing_house'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    post_code = db.Column(db.String(6), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    books = db.relationship('Book', back_populates='publish_house', cascade='all, delete-orphan')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    isbn = db.Column(db.BigInteger, nullable=False, unique=True)
    number_of_pages = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    cena = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', back_populates='books')
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', back_populates='books')
    publish_house_id = db.Column(db.Integer, db.ForeignKey('publishing_house.id'), nullable=False)
    publish_house = db.relationship('PublishingHouse', back_populates='books')
    loans = db.relationship('Loans', back_populates='book')
    orders = db.relationship('Orders', back_populates='book')
    booksinshop = db.relationship('BooksInShop', back_populates='book', cascade="all, delete-orphan")

    def __init__(self, ti, isbn, nop, desc, pr, aid, cid, phid):
        self.title = ti
        self.isbn = isbn
        self.number_of_pages = nop
        self.description = desc
        self.cena = pr
        self.author_id = aid
        self.category_id = cid
        self.publish_house_id = phid

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Loans(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book = db.relationship('Book', back_populates='loans')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='loans')
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, default=(datetime.utcnow() + timedelta(days=30)))
    price = db.Column(db.Integer, nullable=False)

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book = db.relationship('Book', back_populates='orders')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='orders')
    buy_date = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class Shop(db.Model):
    __tablename__ = 'shops'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    post_code = db.Column(db.String(6), nullable=False)
    booksinshop = db.relationship('BooksInShop', back_populates='shop')

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class BooksInShop(db.Model):
    __tablename__ = 'booksinshop'
    id = db.Column(db.Integer, primary_key=True)
    shop_id = db.Column(db.Integer, db.ForeignKey('shops.id'), nullable=False)
    shop = db.relationship('Shop', back_populates='booksinshop')
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    book = db.relationship('Book', back_populates='booksinshop')
    how_many = db.Column(db.Integer, nullable=False)

    @staticmethod
    def additional_validation(param: str, value: str) -> str:
        return value


class AuthorForm(FlaskForm):
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    birth_date = DateField("Birth Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password1 = PasswordField("Password", validators=[DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class BookForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    isbn = IntegerField("ISBN", validators=[DataRequired()])
    number_of_pages = IntegerField("Number of Pages", validators=[DataRequired()])
    description = StringField("Description")
    cena = IntegerField("Price", validators=[DataRequired()])
    author_id = IntegerField("Author", validators=[DataRequired()])
    category_id = IntegerField("Category", validators=[DataRequired()])
    publish_house_id = IntegerField("Publishing House", validators=[DataRequired()])
    submit = SubmitField("Submit")


class FindBookForm(FlaskForm):
    author = SelectField("Author", validators=[DataRequired()])
    category = SelectField("Category", validators=[DataRequired()])
    publish_house = SelectField("Publish House", validators=[DataRequired()])
    submit = SubmitField("Submit")


class OrderForm(FlaskForm):
    book_id = IntegerField("Book", validators=[DataRequired()])
    user_id = IntegerField("User", validators=[DataRequired()])
    shop_id = SelectField("Shop", validators=[DataRequired()])
    submit = SubmitField("Submit")


class ShopForm(FlaskForm):
    city = StringField("City", validators=[DataRequired()])
    street = StringField("Street", validators=[DataRequired()])
    post_code = StringField("Post code", validators=[DataRequired()])
    submit = SubmitField("Submit")

    @validates('post_code')
    def validate_post_code(self, value):
        if len(str(value)) != 6:
            raise ValidationError('Post code must contains 6 characters')


class BookInShopForm(FlaskForm):
    shop = IntegerField("Shop", validators=[DataRequired()])
    book = SelectField("Book", validators=[DataRequired()])
    how_many = IntegerField("How Many", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AuthorSchema(Schema):
    id = fields.Integer(dump_only=True)
    first_name = fields.String(required=True, validate=validate.Length(max=50))
    last_name = fields.String(required=True, validate=validate.Length(max=50))
    birth_date = fields.Date('%Y-%m-%d', required=True)
    books = fields.List(fields.Nested(lambda: BookSchema(exclude=['author'])))

    @validates('birth_date')
    def validate_birth_date(self, value):
        if value > datetime.now().date():
            raise ValidationError('Birth date must be lower than {datetime.now().date()}')


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True, validate=validate.Length(max=255))
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, dump_only=True, validate=validate.Length(min=6, max=255))
    creation_date = fields.DateTime(dump_only=True)


class UserPasswordUpdate(Schema):
    current_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))
    new_password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=255))
    books = fields.List(fields.Nested(lambda: BookSchema(only=['title'])))


class PublishingHouseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=255))
    city = fields.String(required=True, validate=validate.Length(max=255))
    post_code = fields.String(required=True, validate=validate.Length(max=6))
    street = fields.String(required=True, validate=validate.Length(max=255))
    email = fields.Email(required=True)
    books = fields.List(fields.Nested(lambda: BookSchema(only=['title'])))

    @validates('post_code')
    def validate_post_code(self, value):
        if len(str(value)) != 6:
            raise ValidationError('Post code must contains 6 characters')


class BookSchema(Schema):
    id = fields.Integer(dump_only=True)
    title = fields.String(required=True, validate=validate.Length(max=50))
    isbn = fields.Integer(required=True)
    number_of_pages = fields.Integer(required=True)
    description = fields.String()
    cena = fields.Integer(required=True)
    author_id = fields.Integer(load_only=True)
    author = fields.Nested(lambda: AuthorSchema(only=['id', 'first_name', 'last_name']))
    category_id = fields.Integer(load_only=True, required=True)
    category = fields.Nested(lambda: CategorySchema(only=['id','name']))
    publish_house_id = fields.Integer(load_only=True, required=True)
    publish_house = fields.Nested(lambda: PublishingHouseSchema(only=['id','name']))

    @validates('isbn')
    def validate_isbn(self, value):
        if len(str(value)) != 13:
            raise ValidationError('ISBN must contains 13 digits')


class LoansSchema(Schema):
    id = fields.Integer(dump_only=True)
    book_id = fields.Integer(load_only=True, required=True)
    book = fields.Nested(lambda: BookSchema(only=['title']))
    user_id = fields.Integer(load_only=True)
    user = fields.Nested(lambda: UserSchema(only=['username']))
    start_date = fields.DateTime(dump_only=True)
    end_date = fields.DateTime(dump_only=True)
    price = fields.Integer(required=True)


class OrdersSchema(Schema):
    id = fields.Integer(dump_only=True)
    book_id = fields.Integer(load_only=True, required=True)
    book = fields.Nested(lambda: BookSchema(only=['title']))
    user_id = fields.Integer(load_only=True, required=True)
    user = fields.Nested(lambda: UserSchema(only=['username']))
    buy_date = fields.DateTime(dump_only=True)


class ShopSchema(Schema):
    id = fields.Integer(dump_only=True)
    city = fields.String(required=True, validate=validate.Length(max=255))
    street = fields.String(required=True, validate=validate.Length(max=255))
    post_code = fields.String(required=True, validate=validate.Length(max=6))
    booksinshop = fields.List(fields.Nested(lambda: BooksInShopSchema(only=['how_many', 'book'])))

    @validates('post_code')
    def validate_post_code(self, value):
        if len(str(value)) != 6:
            raise ValidationError('Post code must contains 6 characters')


class BooksInShopSchema(Schema):
    id = fields.Integer(dump_only=True)
    book_id = fields.Integer(load_only=True, required=True)
    book = fields.Nested(lambda: BookSchema(only=['title']))
    shop_id = fields.Integer(load_only=True, required=True)
    shop = fields.Nested(lambda: ShopSchema(only=['city']))
    how_many = fields.Integer(required=True)


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
user_password_update_schema = UserPasswordUpdate()
category_schema = CategorySchema()
publishing_house_schema = PublishingHouseSchema()
book_schema = BookSchema()
books_schema = BookSchema(many=True)
loans_schema = LoansSchema()
order_schema = OrdersSchema()
shop_schema = ShopSchema()
booksinshops_schema = BooksInShopSchema()
