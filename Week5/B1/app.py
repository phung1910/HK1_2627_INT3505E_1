from flask import Flask, jsonify
from models import db, Category, Author
from books import bp as books_bp


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bookstore.db"
    db.init_app(app)
    app.register_blueprint(books_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="not_found"), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="bad_request"), 400

    with app.app_context():
        db.create_all()
        if not db.session.scalar(db.select(Category)):   # seed 1 lần
            db.session.add_all([
                Category(name="Technology", slug="tech"),
                Author(name="Robert C. Martin", bio="Uncle Bob"),
                Author(name="Martin Fowler", bio="Refactoring"),
            ])
            db.session.commit()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)