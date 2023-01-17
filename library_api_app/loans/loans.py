from flask import abort, jsonify, render_template, flash
from webargs.flaskparser import use_args

from library_api_app import db, login_manager
from library_api_app.loans import loans_bp
from library_api_app.models import Loans, LoansSchema, loans_schema, User, Book, OrderForm, Shop, BooksInShop
from library_api_app.utils import validate_json_content_type, token_required
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from library_api_app.loans.tasks import askforuser, askforBook, askforbookinshop, bookinshopupdate, writeLoan

login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@loans_bp.route('/loans/<int:book_id>', methods=['POST'])
@login_required
def create_loan(book_id):
    loan = Loans(user_id=current_user.id, book_id=book_id, price=5)
    print(loan.id)
    db.session.add(loan)
    db.session.commit()

    return jsonify({"message":"Object successfully added to database"})


@loans_bp.route('/loans/<int:user1_id>', methods=['GET'])
def get_all_user_loans(user1_id: int):
    User.query.get_or_404(user1_id, description=f'User with id {user1_id} not found')
    loans = Loans.query.filter(Loans.user_id == user1_id).all()

    items = LoansSchema(many=True, exclude=['user']).dump(loans)

    return jsonify(items)