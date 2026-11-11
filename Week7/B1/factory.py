from flask import Flask

from extensions import db, api
from config import DefaultConfig
from errors import register_error_handlers
from api.products import blp as products_blp


def create_app(config=None):
    """Gọi được nhiều lần — mỗi lần tạo 1 app độc lập (slide 8: Application Factory)."""
    app = Flask(__name__)
    app.config.from_object(config or DefaultConfig)

    db.init_app(app)
    api.init_app(app)          # flask-smorest: gắn Api vào app, dựng OpenAPI/Swagger
    api.register_blueprint(products_blp)   # không phải app.register_blueprint!

    register_error_handlers(app)

    with app.app_context():
        db.create_all()        # demo only — production dùng Flask-Migrate (slide 17)

    return app
