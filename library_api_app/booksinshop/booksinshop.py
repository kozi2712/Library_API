from flask import jsonify, request, render_template, flash, redirect, url_for
from webargs.flaskparser import use_args

from library_api_app import db
from library_api_app.models import BooksInShop, BooksInShopSchema, booksinshops_schema, BookInShopForm, Shop, Book
from library_api_app.utils import validate_json_content_type, get_schema_args, apply_orders, apply_filter, get_pagination, token_required
from library_api_app.booksinshop import booksinshop_bp


@booksinshop_bp.route('/addbookstoshop/<int:shop_id>/<int:book_id>', methods=['GET', 'POST'])
def add(shop_id, book_id):
    form = BookInShopForm()
    if request.method == "POST":
        bookinshop = BooksInShop.query.filter(BooksInShop.shop_id == form.shop.data,
                                              BooksInShop.book_id == form.book.data).first()

        shop = Shop.query.get_or_404(shop_id, description=f'Shop with id {shop_id} not found')
        booksinshop = BooksInShop.query.filter(BooksInShop.shop_id == shop_id).all()
        books = Book.query.all()

        bookinshop.how_many = bookinshop.how_many + form.how_many.data

        db.session.commit()
        return render_template("shopcred.html", shop=shop, books=booksinshop, book=books)
    else:
        return render_template("addmorebooks.html", form=form, shop_id=shop_id, book_id=book_id)


@booksinshop_bp.route('/addbookstoshop/<int:shop_id>', methods=['GET', 'POST'])
def create(shop_id):
    form = BookInShopForm()
    form.book.choices = [(book.id, book.title) for book in Book.query.all()]
    if request.method == "POST":
        bookinshop = BooksInShop.query.filter(BooksInShop.shop_id == form.shop.data,
                                              BooksInShop.book_id == form.book.data).first()

        if bookinshop is not None:
            flash("połączenie w bazie już istnieje")
            return redirect(url_for('shops.get_shops'))
        shop = Shop.query.get_or_404(shop_id, description=f'Shop with id {shop_id} not found')
        booksinshop = BooksInShop.query.filter(BooksInShop.shop_id == shop_id).all()
        books = Book.query.all()

        if bookinshop is None:
            print(1)
            bookinshop = BooksInShop(
                shop_id=form.shop.data,
                book_id=form.book.data,
                how_many=form.how_many.data
            )

            db.session.add(bookinshop)
            db.session.commit()
            return render_template("shopcred.html", shop=shop, books=booksinshop, book=books)
        else:
            bookinshop.how_many = bookinshop.how_many + form.how_many.data
        db.session.commit()
        return render_template("shopcred.html", shop=shop, books=booksinshop, book=books)
    else:
        return render_template("addmorebooks.html", form=form, shop_id=shop_id)


@booksinshop_bp.route('/booksinshop', methods=['GET'])
def get_bis():
    query = BooksInShop.query
    schema_args = get_schema_args(BooksInShop)
    query = apply_orders(BooksInShop, query)
    query = apply_filter(BooksInShop, query)
    items, pagination = get_pagination(query, 'booksinshop.get_bis')

    booksinshop = BooksInShopSchema(**schema_args).dump(items)

    return jsonify({
        'success': True,
        'data': booksinshop,
        'number_of_records': len(booksinshop),
        'pagination': pagination
    })


@booksinshop_bp.route('/booksinshop', methods=['POST'])
@token_required
@validate_json_content_type
@use_args(booksinshops_schema, error_status_code=400)
def add_author(user_id: int, args: dict):

    bis = BooksInShop(**args)
    db.session.add(bis)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': booksinshops_schema.dump(bis)
    }), 201
