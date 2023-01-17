from flask import abort, jsonify, render_template, flash, request, redirect, url_for
from webargs.flaskparser import use_args

from library_api_app import db, login_manager
from library_api_app.auth import auth_bp
from library_api_app.models import User, user_schema, user_password_update_schema, UserForm, LoginForm, Orders, Loans, Book
from flask_login import login_user, login_required, logout_user, current_user


login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/xd', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template("base.html")


@auth_bp.route('/register', methods=['POST'])
def register():

    username = request.json['username']
    email = request.json['email']
    pwd1 = request.json['password1']
    pwd2 = request.json['password2']

    if pwd1 != pwd2:
        abort(403)

    user_exists = User.query.filter_by(email=email).first() is not None

    if user_exists:
        abort(409)
        return jsonify(user_schema.dump(user_exists))

    pwd1 = User.generate_hashed_password(pwd1)
    new_user = User(username, email, pwd1)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_schema.dump(new_user))


@auth_bp.route('/login', methods=['POST'])
def login():

    username = request.json['username']
    pwd1 = request.json['password1']

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({"error": "Unauthorized"}), 401
    if user.is_password_valid(pwd1):
        login_user(user)
        token = user.generate_jwt()
        flash("login succeeded")
        return jsonify(access_token=token)
    else:
        flash("Wrong password, try again!")
        return jsonify({"error": "Unauthorized"})


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been log out!")
    return redirect(url_for('auth.login'))


@auth_bp.route('/user', methods=['GET', 'POST'])
@login_required
def get_current_user():
    orders = Orders.query.filter(Orders.user_id == current_user.id).order_by(Orders.buy_date)
    loans = Loans.query.filter(Loans.user_id == current_user.id).order_by(Loans.start_date)
    books = Book.query.all()
    return render_template("usercred.html", orders=orders, loans=loans, books=books)


@auth_bp.route('/modifypassword/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id: int):
    form = UserForm()
    user_to_update = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")
    if request.method == "POST":

        user = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

        if user.is_password_valid(request.form['password1']):
            user.password = user.generate_hashed_password(request.form['password2'])
            flash("User updated successfully")
        else:
            flash("Wrong password")

        db.session.commit()
        return render_template("updtpwd.html", form=form, user_to_update=user_to_update)
    else:
        return render_template("updtpwd.html", form=form, user_to_update=user_to_update, user_id=user_id)


@auth_bp.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update_user_data(user_id: int):
    form = UserForm()
    user_to_update = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")
    if request.method == "POST":
        if User.query.filter(User.username == request.form['username']).first():
            abort(409, description=f'User with username {request.form["username"]} already exists')
        if User.query.filter(User.email == request.form['email']).first():
            abort(409, description=f'User with email {request.form["email"]} already exists')

        user = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash("User updated successfully")
        return render_template("updateuser.html", form=form, user_to_update=user_to_update, user_id=user_id)

    else:
        return render_template("updateuser.html", form=form, user_to_update=user_to_update, user_id=user_id)


@auth_bp.route('/delete/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        return jsonify({"success":"user deleted successfully"})

    except:
        return jsonify({"error":"there was a problem with deleting user"})


@auth_bp.route('/update/password', methods=['PUT'])
@use_args(user_password_update_schema, error_status_code=400)
def update_user_password(user_id: int, args: dict):
    user = User.query.get_or_404(user_id, description=f"User with id {user_id} not found")

    if not user.is_password_valid(args['current_password']):
        abort(401, description="Invalid password")

    user.password = user.generate_hashed_password(args['new_password'])
    db.session.commit()

    return jsonify({
        'success': True,
        'data': user_schema.dump(user)
    })