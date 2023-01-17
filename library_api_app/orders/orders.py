from flask import jsonify, render_template, flash
from library_api_app import db, login_manager
from library_api_app.orders import orders_bp
from library_api_app.models import Orders, OrdersSchema, User, Book, OrderForm, Shop
from library_api_app.tasks import askforuser
from flask_login import login_required, current_user
from library_api_app.orders.tasks import askforuser, askforBook, askforbookinshop, bookinshopupdate, writeOrder

login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@orders_bp.route('/orders/<int:book_id>', methods=['GET', 'POST'])
@login_required
def create_order(book_id):
    form = OrderForm()
    form.shop_id.choices = [(shop.id, shop.city) for shop in Shop.query.all()]
    if form.validate_on_submit():
        u = askforuser.delay(current_user.id)
        u.get()
        b = askforBook.delay(book_id)
        b.get()
        bw = askforbookinshop.delay(book_id, form.shop_id.data)
        bw.get()

        writeOrder.delay(current_user.id, form.book_id.data)

        books = Book.query.order_by(Book.id)
        if bw.get() == -1:
            flash("podany sklep nie posiada danej ksiazki")
            return render_template("books.html", our_books=books)
        else:
            if bw.get() == 0:
                flash("w danym sklepie nie ma juz tej ksiazki")
                return render_template("books.html", our_books=books)
            else:
                bookinshopupdate.delay(book_id, form.shop_id.data)

        db.session.commit()

        form.user_id.data = ''
        form.book_id.data = ''
        flash("Zamówienie zostało złożone pomyślnie")

    return render_template("order.html", form=form, user_id=current_user.id, book_id=book_id)


@orders_bp.route('/orders/<int:user1_id>', methods=['GET'])
def get_all_user_orders(user1_id: int):
    User.query.get_or_404(user1_id, description=f'User with id {user1_id} not found')
    order = Orders.query.filter(Orders.user_id == user1_id).all()

    items = OrdersSchema(many=True, exclude=['user']).dump(order)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })