from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity

from models import db, Order


def require_roles(*allowed):
    """slide 24 — Decorator 1: roles (OR), coarse."""
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            urs = set(get_jwt().get("roles", []))
            if not urs & set(allowed):
                return jsonify({
                    "error": "forbidden",
                    "need_one_of": list(allowed),
                }), 403
            return fn(*a, **kw)
        return w
    return d


def require_scopes(*needed):
    """slide 25 — Decorator 2: scopes (AND), fine per request."""
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            granted = set(get_jwt().get("scopes", []))
            if not set(needed).issubset(granted):
                return jsonify({
                    "error": "insufficient_scope",
                    "need_all_of": list(needed),
                }), 403
            return fn(*a, **kw)
        return w
    return d


def user_owns_resource(param="id"):
    """slide 26 — Decorator 3: ownership, chống BOLA (OWASP API1)."""
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            order = db.session.get(Order, kw[param])
            if order is None:
                return jsonify({"error": "not_found"}), 404
            uid = get_jwt_identity()
            roles = set(get_jwt().get("roles", []))
            if str(order.owner_id) != str(uid) and "admin" not in roles:
                return jsonify({"error": "forbidden"}), 403
            return fn(*a, **kw)
        return w
    return d
