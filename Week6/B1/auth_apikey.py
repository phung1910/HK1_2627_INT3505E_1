import hashlib
import secrets
from functools import wraps

from flask import Blueprint, request, jsonify, g

from models import db, ApiKey, Order

bp = Blueprint("auth_apikey", __name__, url_prefix="/api")


def mint_key(prefix, owner_id, scopes):
    """slide 10 — CSPRNG key + sha256 hash lưu DB, trả plaintext 1 lần."""
    raw = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8]
    plain = f"{prefix}_{raw}_{digest}"
    stored = hashlib.sha256(plain.encode()).hexdigest()
    key = ApiKey(prefix=prefix, hash=stored, last4=plain[-4:],
                 owner_id=owner_id, scopes=",".join(scopes))
    db.session.add(key)
    db.session.commit()
    return plain, key


def require_api_key(scopes=None):
    """slide 11-12 — verify key, check revoked, check scope."""
    def d(fn):
        @wraps(fn)
        def w(*a, **kw):
            key = request.headers.get("X-Api-Key", "")
            if not key:
                return jsonify({"error": "missing"}), 401
            hashed = hashlib.sha256(key.encode()).hexdigest()
            row = db.session.scalar(db.select(ApiKey).filter_by(hash=hashed))
            if row is None or row.revoked_at is not None:
                return jsonify({"error": "invalid"}), 401
            granted = set(row.scopes.split(","))
            if scopes and not set(scopes).issubset(granted):
                return jsonify({"error": "scope"}), 403
            g.api_key_id = row.id
            g.owner_id = row.owner_id
            g.api_scopes = granted
            return fn(*a, **kw)
        return w
    return d


@bp.post("/keys")
def create_key():
    """Mint key demo cho user cố định (owner_id=1 = an@vnu.edu.vn)."""
    payload = request.get_json(silent=True) or {}
    scopes = payload.get("scopes", ["orders:read"])
    plain, key = mint_key("sk_demo", owner_id=1, scopes=scopes)
    return jsonify(key=plain, last4=key.last4, scopes=scopes), 201


@bp.get("/apikey/orders")
@require_api_key(scopes=["orders:read"])
def list_orders_apikey():
    rows = db.session.scalars(
        db.select(Order).filter_by(owner_id=g.owner_id)
    ).all()
    return jsonify(orders=[o.to_dict() for o in rows])
