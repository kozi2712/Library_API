from flask import jsonify
from celery import shared_task
from library_api_app.models import User, Book, BooksInShop, Orders
from library_api_app import db


@shared_task
def divide(x, y):
    import time
    time.sleep(5)
    return x/y


@shared_task
def askforuser(user_id: int):
    user = User.query.get_or_404(user_id)
    return user.id


@shared_task
def askforBook(book_id):
    book = Book.query.get_or_404(book_id, description=f'Book with id {book_id} not found')
    return book.id


@shared_task
def askforbookinshop(book_id, shop_id):
    bookwhere = BooksInShop.query.filter(BooksInShop.book_id == book_id,
                                         BooksInShop.shop_id == shop_id).first()
    if bookwhere is None:
        return -1
    else:
        return bookwhere.how_many


@shared_task
def bookinshopupdate(book_id, shop_id):
    bookwhere = BooksInShop.query.filter(BooksInShop.book_id == book_id,
                                         BooksInShop.shop_id == shop_id).first()
    bookwhere.how_many = bookwhere.how_many - 1
    db.session.commit()
    return bookwhere.how_many


@shared_task
def writeOrder(user_id, book_id):
    order = Orders(user_id=user_id, book_id=book_id)
    print(order.id)
    db.session.add(order)
    db.session.commit()
    return 'zamowienie zapisane do bazy'


@shared_task
def BookList():
    books = Book.query.order_by(Book.id)
    return jsonify({
        'data': books
    })
