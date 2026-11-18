from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)

from models import db, User, Order
from security import verify_password
from rbac import require_roles, require_scopes, user_owns_resource

bp = Blueprint("auth_jwt", __name__, url_prefix="/api")

# slide 15: production nên lưu blocklist trong Redis (@jwt.token_in_blocklist_loader
# đọc redis.get(f"revoked:{jti}")). Ở đây dùng dict in-memory để demo chạy được
# không cần service ngoài; cùng ý tưởng revoke theo jti.
REVOKED_JTI = set()


def register_jwt_callbacks(jwt):
    @jwt.token_in_blocklist_loader
    def check_revoked(_header, payload):
        return payload["jti"] in REVOKED_JTI


def _load_permissions(user: User):
    """slide 16 — helper trả {"roles": [...], "scopes": [...]}."""
    return {"roles": user.roles_list(), "scopes": user.scopes_list()}


@bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    user = db.session.scalar(
        db.select(User).filter_by(email=payload.get("email"))
    )
    password = payload.get("password", "")
    if not user or not verify_password(password, user.pwd_hash):
        return jsonify(error="invalid_credentials"), 401

    claims = _load_permissions(user)
    uid = str(user.id)
    return jsonify(
        access=create_access_token(identity=uid, additional_claims=claims),
        refresh=create_refresh_token(identity=uid, additional_claims=claims),
    )


@bp.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    user = db.session.get(User, int(get_jwt_identity()))
    claims = _load_permissions(user)
    return jsonify(access=create_access_token(
        identity=get_jwt_identity(), additional_claims=claims))


@bp.post("/auth/logout")
@jwt_required()
def logout():
    """slide 15 ghi 'route logout cần bổ sung' — lab thêm để demo revocation."""
    REVOKED_JTI.add(get_jwt()["jti"])
    return "", 204


@bp.get("/jwt/orders")
@jwt_required()
def list_orders_jwt():
    """slide 17 — check scope từ claims."""
    uid = get_jwt_identity()
    claims = get_jwt()
    if "orders:read" not in claims.get("scopes", []):
        return jsonify(error="insufficient_scope"), 403
    rows = db.session.scalars(
        db.select(Order).filter_by(owner_id=int(uid))
    ).all()
    return jsonify(orders=[o.to_dict() for o in rows])


@bp.delete("/jwt/orders/<int:id>")
@jwt_required()
@require_roles("admin", "manager")
@require_scopes("orders:write")
@user_owns_resource("id")
def delete_order_jwt(id):
    """slide 25 — 3 lớp check chồng lên 1 route (AuthN -> role -> scope -> ownership)."""
    order = db.session.get(Order, id)
    db.session.delete(order)
    db.session.commit()
    return "", 204
