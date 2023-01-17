from flask import jsonify, render_template, request, flash
from webargs.flaskparser import use_args

from library_api_app import db
from library_api_app.models import Shop, ShopSchema, shop_schema, ShopForm, BooksInShop, Book
from library_api_app.utils import validate_json_content_type, get_schema_args, apply_orders, apply_filter, get_pagination, token_required
from library_api_app.shops import shops_bp


@shops_bp.route('/shops', methods=['GET'])
def get_shops():
    shops = Shop.query.order_by(Shop.id)
    return render_template("shops.html", shops=shops)


@shops_bp.route('/shops/<int:shops_id>', methods=['GET'])
def get_shop(shops_id: int):

    shop = Shop.query.get_or_404(shops_id, description=f'Shop with id {shops_id} not found')
    booksinshop = BooksInShop.query.filter(BooksInShop.shop_id == shops_id).all()
    books = Book.query.all()
    return render_template("shopcred.html", shop=shop, books=booksinshop, book=books)


@shops_bp.route('/shops/update/<int:shops_id>', methods=['GET', 'POST'])
def update_shop(shops_id: int):
    form = ShopForm()
    shop = Shop.query.get_or_404(shops_id, description=f'Shop with id {shops_id} not found')
    if request.method == "POST":
        shop.city = request.form['city']
        shop.post_code = request.form['post_code']
        shop.street = request.form['street']

        db.session.commit()
        flash("Shop updated successfully")
        return render_template("modShop.html", form=form, shop=shop, shop_id=shops_id)
    else:
        return render_template("modShop.html", form=form, shop=shop, shop_id=shops_id)


@shops_bp.route('/shops/delete/<int:shop_id>')
def delete_shop(shop_id: int):
    shop = Shop.query.get_or_404(shop_id, description=f'Shop with id {shop_id} not found')
    try:
        db.session.delete(shop)
        db.session.commit()
        flash("Shop deleted successfully")
        shops = Shop.query.order_by(Shop.id)
        return render_template("shops.html", shops=shops)
    except:
        flash("there was a problem with deleting shop")
        shops = Shop.query.order_by(Shop.id)
        return render_template("shops.html", shops=shops)


@shops_bp.route('/shops', methods=['POST'])
@token_required
@validate_json_content_type
@use_args(shop_schema, error_status_code=400)
def add_shop(user_id: int, args: dict):

    shop = Shop(**args)
    db.session.add(shop)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': shop_schema.dump(shop)
    }), 201