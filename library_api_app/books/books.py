from flask import jsonify, abort, render_template, flash, request
from library_api_app.books import books_bp
from library_api_app import db, login_manager
from library_api_app.models import Book, BookSchema, Author, Category, PublishingHouse, BookForm, FindBookForm, User, books_schema, book_schema
from flask_login import login_required


login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@books_bp.route('/book', methods=['GET'])
def get_books():
    books = Book.query.order_by(Book.id)
    results = books_schema.dump(books)
    return jsonify(results)


@books_bp.route('/book/<int:book_id>', methods=['GET'])
def get_book(book_id: int):
    book = Book.query.get_or_404(book_id, description=f'Book with id {book_id} not found')
    author = Author.query.get_or_404(book.author_id)
    ct = Category.query.get_or_404(book.category_id)
    ph = PublishingHouse.query.get_or_404(book.publish_house_id)
    return render_template("bookcred.html", our_book=book, author=author, ct=ct, ph=ph)


@books_bp.route('/book/<int:book_id>', methods=['PUT'])
def update_book(book_id: int):
    book = Book.query.get(book_id)

    book.title = request.json['title']
    book.isbn = request.json['isbn']
    book.number_of_pages = request.json['number_of_pages']
    book.cena = request.json['cena']
    description = request.json['description']
    if description is not None:
        book.description = description
    author_id = request.json['author_id']
    if author_id is not None:
        Author.query.get(author_id)
        book.author_id = author_id
    category_id = request.json['category_id']
    if category_id is not None:
        Category.query.get(category_id)
        book.category_id = category_id
    publish_house_id = request.json['publish_house_id']
    if publish_house_id is not None:
        PublishingHouse.query.get(publish_house_id)
        book.publish_house_id = publish_house_id

    db.session.commit()
    return jsonify(book_schema.dump(book))


@books_bp.route('/book/<int:book_id>', methods=['DELETE'])
def delete_book(book_id: int):
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()
    #return jsonify(book_schema.dump(book))



@books_bp.route('/book', methods=['POST'])
def create_book():

    title = request.json['title']
    isbn = request.json['isbn']
    nop = request.json['number_of_pages']
    dsc = request.json['description']
    pr = request.json['cena']
    aid = request.json['author_id']
    cid = request.json['category_id']
    phid = request.json['publish_house_id']

    if Book.query.filter(Book.isbn == isbn).first():
        abort(409, description=f'Book with ISBN {request.form["isbn"]} already exists')

    book = Book(
        title,
        isbn,
        nop,
        dsc,
        pr,
        aid,
        cid,
        phid
    )
    db.session.add(book)
    db.session.commit()

    return jsonify(book_schema.dump(book))


@books_bp.route('findbook', methods=['GET', 'POST'])
def find_book():
    form = FindBookForm()
    form.author.choices = [(author.id, author.first_name+author.last_name) for author in Author.query.all()]
    form.category.choices = [(category.id, category.name) for category in Category.query.all()]
    form.publish_house.choices = [(pubhouse.id, pubhouse.name) for pubhouse in PublishingHouse.query.all()]
    if form.validate_on_submit():
        books = Book.query.filter(Book.author_id == form.author.data,
                                  Book.category_id == form.category.data,
                                  Book.publish_house_id == form.publish_house.data).all()
        if books is None:
            flash("Nie znaleziono żadnej książki")
            return render_template("books.html", our_books=books)
        else:
            return render_template("books.html", our_books=books)
    return render_template("findbook.html", form=form)


@books_bp.route('/authors/<int:author_id>/books', methods=['GET'])
def get_all_author_books(author_id: int):
    Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')
    books = Book.query.filter(Book.author_id == author_id).all()

    items = BookSchema(many=True, exclude=['author']).dump(books)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })


@books_bp.route('/category/<int:category_id>/books', methods=['GET'])
def get_all_category_books(category_id: int):
    Category.query.get_or_404(category_id, description=f'Category with id {category_id} not found')
    books = Book.query.filter(Book.category_id == category_id).all()

    items = BookSchema(many=True, exclude=['category']).dump(books)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })


@books_bp.route('/publishing_house/<int:house_id>/books', methods=['GET'])
def get_all_house_books(house_id: int):
    PublishingHouse.query.get_or_404(house_id, description=f'House with id {house_id} not found')
    books = Book.query.filter(Book.publish_house_id == house_id).all()

    items = BookSchema(many=True, exclude=['publish_house']).dump(books)

    return jsonify({
        'success': True,
        'data': items,
        'number_of_records': len(items)
    })
