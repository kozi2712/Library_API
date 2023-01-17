import json
from pathlib import Path
from datetime import datetime
from library_api_app import db
from library_api_app.models import Author, Category, PublishingHouse, Book, Shop, BooksInShop
from library_api_app.commands import db_manage_bp


def load_json_data(file_name: str) -> list:
    json_path = Path(__file__).parent.parent / 'samples' / file_name
    with open(json_path) as file:
        data_json = json.load(file)
    return data_json


@db_manage_bp.cli.group()
def db_manage():
    """Database management commands"""
    pass


@db_manage.command()
def add_data():
    """Add sample data from the database"""
    try:
        data_json = load_json_data('authors.json')
        for item in data_json:
            item['birth_date'] = datetime.strptime(item['birth_date'], '%d-%m-%Y').date()
            author = Author(**item)
            db.session.add(author)

        data_json = load_json_data('categories.json')
        for item in data_json:
            category = Category(**item)
            db.session.add(category)

        data_json = load_json_data('publish_house.json')
        for item in data_json:
            publish_house = PublishingHouse(**item)
            db.session.add(publish_house)

        data_json = load_json_data('books.json')
        for item in data_json:
            books = Book(**item)
            db.session.add(books)

        data_json = load_json_data('shops.json')
        for item in data_json:
            shops = Shop(**item)
            db.session.add(shops)

        data_json = load_json_data('booksinshop.json')
        for item in data_json:
            booksinshop = BooksInShop(**item)
            db.session.add(booksinshop)

        db.session.commit()
        print('Data has been successfully added to database')
    except Exception as exc:
        print("Unexpected error: {}".format(exc))


@db_manage.command()
def remove_data():
    """Remove all data to database"""
    try:
        db.session.execute('DELETE FROM loans')
        db.session.execute('ALTER TABLE loans AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM orders')
        db.session.execute('ALTER TABLE orders AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM booksinshop')
        db.session.execute('ALTER TABLE booksinshop AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM books')
        db.session.execute('ALTER TABLE books AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM category')
        db.session.execute('ALTER TABLE category AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM authors')
        db.session.execute('ALTER TABLE authors AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM Publishing_house')
        db.session.execute('ALTER TABLE Publishing_house AUTO_INCREMENT = 1')
        db.session.execute('DELETE FROM shops')
        db.session.execute('ALTER TABLE shops AUTO_INCREMENT = 1')
        db.session.commit()
        print('Data has been successfully removed from database')
    except Exception as exc:
        print("Unexpected error: {}".format(exc))
