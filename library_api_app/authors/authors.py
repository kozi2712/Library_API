from flask import render_template, flash, request, jsonify
from library_api_app import db, login_manager
from library_api_app.models import Author, AuthorForm, User, authors_schema, author_schema
from library_api_app.authors import authors_bp
from flask_login import login_required

login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@authors_bp.route('/author', methods=['GET'])
def get_authors():
    authors = Author.query.order_by(Author.id)
    results = authors_schema.dump(authors)
    return jsonify(results)


@authors_bp.route('/authors/<int:author_id>', methods=['GET'])
@login_required
def get_author(author_id: int):
    author = Author.query.get_or_404(author_id, description=f'Author with id {author_id} not found')
    return render_template("authorcreds.html", our_author=author)


@authors_bp.route('/author', methods=['POST'])
def add_author():
    first_name = request.json['first_name']
    last_name = request.json['last_name']
    birth_date = request.json['birth_date']

    author = Author(first_name,last_name,birth_date)
    db.session.add(author)
    db.session.commit()
    return jsonify(author_schema.dump(author))


@authors_bp.route('/author/<id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get(id)

    author.first_name = request.json['first_name']
    author.last_name = request.json['last_name']
    author.birth_date = request.json['birth_date']

    db.session.commit()
    return jsonify(author_schema.dump(author))


@authors_bp.route('/author/<int:author_id>', methods=['DELETE'])
def delete_author(author_id: int):
    author = Author.query.get(author_id)
    db.session.delete(author)
    db.session.commit()

    return jsonify(author_schema.dump(author))

