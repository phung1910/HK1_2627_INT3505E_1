from flask import Blueprint, jsonify
from flask_httpauth import HTTPBasicAuth

from models import db, User, Order
from security import verify_password

auth = HTTPBasicAuth()
bp = Blueprint("auth_basic", __name__, url_prefix="/api/basic")


@auth.verify_password
def verify(email, password):
    user = db.session.scalar(db.select(User).filter_by(email=email))
    if user is None:
        return None
    return user if verify_password(password, user.pwd_hash) else None


@auth.error_handler
def on_auth_error(status):
    return jsonify({"error": "unauthorized"}), 401, {
        "WWW-Authenticate": 'Basic realm="orders"'
    }


@bp.get("/orders")
@auth.login_required
def list_orders():
    """slide 8 — route protected bằng Basic Auth, trả orders + principal."""
    user = auth.current_user()
    rows = db.session.scalars(
        db.select(Order).filter_by(owner_id=user.id)
    ).all()
    return jsonify(orders=[o.to_dict() for o in rows],
                   principal={"id": user.id, "email": user.email})
