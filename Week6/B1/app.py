from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from models import db, User, Order
from security import hash_password
from auth_basic import bp as basic_bp
from auth_apikey import bp as apikey_bp
from auth_jwt import bp as jwt_bp, register_jwt_callbacks


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
    app.config["JWT_SECRET_KEY"] = "week6-demo-secret-change-me"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 900          # slide 15: 15 phút
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 2592000      # slide 15: 30 ngày
    app.config["JWT_ALGORITHM"] = "HS256"

    db.init_app(app)
    jwt = JWTManager(app)
    register_jwt_callbacks(jwt)

    app.register_blueprint(basic_bp)
    app.register_blueprint(apikey_bp)
    app.register_blueprint(jwt_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="not_found"), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error="bad_request"), 400

    with app.app_context():
        db.create_all()
        if not db.session.scalar(db.select(User)):   # seed 1 lần
            an = User(email="an@vnu.edu.vn",
                      pwd_hash=hash_password("correct horse battery staple"),
                      roles="admin", scopes="orders:read,orders:write")
            binh = User(email="binh@vnu.edu.vn",
                        pwd_hash=hash_password("secret123"),
                        roles="viewer", scopes="orders:read")
            chau = User(email="chau@vnu.edu.vn",
                        pwd_hash=hash_password("manager123"),
                        roles="manager", scopes="orders:read,orders:write")
            db.session.add_all([an, binh, chau])
            db.session.flush()
            db.session.add_all([
                Order(item="Clean Code x1", amount=120000, owner_id=an.id),
                Order(item="Refactoring x1", amount=150000, owner_id=binh.id),
            ])
            db.session.commit()
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000, use_reloader=False)
