import base64
import json
import os

from flask import Blueprint, request, jsonify, abort, make_response
from jsonschema import validate, ValidationError
from sqlalchemy import func, tuple_

from models import db, Book, Author, BookAuthor, Category, Review

DEFAULT_LIMIT, MAX_LIMIT = 20, 100


def _encode_cursor(state):
    raw = json.dumps(state).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _decode_cursor(token):
    pad = "=" * (-len(token) % 4)
    raw = base64.urlsafe_b64decode(token + pad)
    return json.loads(raw)


def _parse_fields(raw):
    if not raw:
        return None
    return {f.strip() for f in raw.split(",") if f.strip()}


# Whitelist sort keys chống SQLi — không bao giờ dùng raw tên cột (slide 23)
SORT_COLUMNS = {"id": Book.id, "price": Book.price_vnd, "title": Book.title,
                 "stock": Book.stock}


def parse_sort(raw):
    """Trả (column, order_by_cols, desc) hợp lệ, hoặc (None, None, None) nếu sort lạ."""
    desc = raw.startswith("-")
    key = raw.lstrip("-")
    if key not in SORT_COLUMNS:
        return None, None, None
    col = SORT_COLUMNS[key]
    cols = [col.desc() if desc else col.asc(),
            Book.id.desc() if desc else Book.id.asc()]
    return col, cols, desc


def apply_cursor(q, raw_cursor, sort, col, desc):
    """Áp điều kiện composite (col, id) từ cursor. Trả (query, error) - error None nếu OK."""
    if not raw_cursor:
        return q, None
    try:
        state = _decode_cursor(raw_cursor)
        v, i = state["v"], state["i"]
    except Exception:
        return None, (jsonify(error="invalid_cursor"), 400)
    if state.get("s") != sort:  # cursor phải khớp sort hiện tại (slide 25)
        return None, (jsonify(error="sort_changed"), 400)
    op = tuple_(col, Book.id).op("<" if desc else ">")
    return q.where(op((v, i))), None


def build_page(items, sort, col, has_more, fields):
    next_cursor = None
    if items and has_more:
        last = items[-1]
        next_cursor = _encode_cursor({"s": sort, "v": getattr(last, col.key), "i": last.id})
    return jsonify(data=[b.to_dict(fields) for b in items],
                    page={"next_cursor": next_cursor, "has_more": has_more})


bp = Blueprint("books", __name__, url_prefix="/api/v1/books")

_schema_path = os.path.join(os.path.dirname(__file__), "book.json")
with open(_schema_path, encoding="utf-8") as f:
    SCHEMA = json.load(f)


def _validate_or_400(payload):
    """Trả (None) nếu OK, hoặc (response, 400) nếu lỗi."""
    if payload is None:
        return jsonify(error="invalid_json"), 400
    try:
        validate(payload, SCHEMA)
    except ValidationError as e:
        return jsonify(error="validation_failed",
                       field=list(e.path), message=e.message), 400
    return None


def _get_book_or_404(bid):
    book = db.session.get(Book, bid)
    if book is None:
        abort(404)
    return book


# ---------- CRUD /books ----------

@bp.get("")
def list_books():
    """Offset/limit pagination (slide 20)."""
    offset = request.args.get("offset", 0, type=int)
    limit = min(request.args.get("limit", DEFAULT_LIMIT, type=int), MAX_LIMIT)
    total = db.session.scalar(db.select(func.count(Book.id)))
    rows = db.session.scalars(
        db.select(Book).order_by(Book.id).offset(offset).limit(limit)
    ).all()
    return jsonify(data=[b.to_dict() for b in rows], pagination={
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_next": offset + limit < total,
    })


@bp.get("/cursor")
def list_books_cursor():
    """Keyset/cursor pagination theo id (slide 21 - Cursor cơ bản)."""
    limit = min(request.args.get("limit", DEFAULT_LIMIT, type=int), MAX_LIMIT)
    after_id = request.args.get("after_id", type=int)

    q = db.select(Book)
    if after_id is not None:
        q = q.where(Book.id > after_id)
    q = q.order_by(Book.id.asc()).limit(limit + 1)  # +1 trick

    rows = db.session.scalars(q).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = rows[-1].id if rows and has_more else None

    return jsonify(data=[b.to_dict() for b in rows], page_info={
        "next_cursor": next_cursor,
        "has_more": has_more,
    })


@bp.get("/seek")
def list_books_seek():
    """Composite/opaque cursor, sort theo price_vnd DESC + id tie-break (slide 21).

    Cursor = base64url({"v": price_vnd, "i": id}) của item cuối trang trước.
    """
    limit = min(request.args.get("limit", DEFAULT_LIMIT, type=int), MAX_LIMIT)
    cursor = request.args.get("cursor")

    q = db.select(Book)
    if cursor:
        try:
            state = _decode_cursor(cursor)
            v, i = state["v"], state["i"]
        except Exception:
            return jsonify(error="invalid_cursor"), 400
        q = q.where(tuple_(Book.price_vnd, Book.id) < (v, i))
    q = q.order_by(Book.price_vnd.desc(), Book.id.desc()).limit(limit + 1)

    rows = db.session.scalars(q).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = (_encode_cursor({"v": rows[-1].price_vnd, "i": rows[-1].id})
                   if rows and has_more else None)

    return jsonify(data=[b.to_dict() for b in rows], page_info={
        "next_cursor": next_cursor,
        "has_more": has_more,
    })


@bp.get("/search")
def search_books():
    """Lab 2: filter (category) + sort whitelist + composite cursor + field selection."""
    limit = min(request.args.get("limit", DEFAULT_LIMIT, type=int), MAX_LIMIT)
    sort = request.args.get("sort", "-id")
    category_id = request.args.get("category", type=int)
    raw_cursor = request.args.get("cursor")
    fields = _parse_fields(request.args.get("fields"))

    col, cols, desc = parse_sort(sort)
    if col is None:
        return jsonify(error="bad_sort"), 400

    q = db.select(Book).order_by(*cols)
    if category_id is not None:
        q = q.where(Book.category_id == category_id)

    q, err = apply_cursor(q, raw_cursor, sort, col, desc)
    if err:
        return err

    rows = db.session.scalars(q.limit(limit + 1)).all()
    has_more = len(rows) > limit
    return build_page(rows[:limit], sort, col, has_more, fields)


@bp.get("/page")
def list_books_page():
    """Page number + Link header theo RFC 8288 (slide 19)."""
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(request.args.get("per_page", DEFAULT_LIMIT, type=int), MAX_LIMIT)

    total = db.session.scalar(db.select(func.count(Book.id)))
    last_page = max((total + per_page - 1) // per_page, 1)
    rows = db.session.scalars(
        db.select(Book).order_by(Book.id)
        .offset((page - 1) * per_page).limit(per_page)
    ).all()

    resp = make_response(jsonify(data=[b.to_dict() for b in rows]))
    base = "/api/v1/books/page"
    links = [f'<{base}?page=1&per_page={per_page}>; rel="first"']
    if page > 1:
        links.append(f'<{base}?page={page - 1}&per_page={per_page}>; rel="prev"')
    if page < last_page:
        links.append(f'<{base}?page={page + 1}&per_page={per_page}>; rel="next"')
    links.append(f'<{base}?page={last_page}&per_page={per_page}>; rel="last"')
    resp.headers["Link"] = ", ".join(links)
    return resp


@bp.post("")
def create_book():
    payload = request.get_json(silent=True)
    err = _validate_or_400(payload)
    if err:
        return err

    cat_id = payload.get("category_id")
    if cat_id is not None and db.session.get(Category, cat_id) is None:
        return jsonify(error="category_not_found"), 400
    if payload.get("isbn") and db.session.scalar(
            db.select(Book).filter_by(isbn=payload["isbn"])):
        return jsonify(error="isbn_exists"), 409

    book = Book(**payload)
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201


@bp.get("/<int:bid>")
def get_book(bid):
    return jsonify(_get_book_or_404(bid).to_dict())


@bp.put("/<int:bid>")
def update_book(bid):
    book = _get_book_or_404(bid)
    payload = request.get_json(silent=True)
    err = _validate_or_400(payload)
    if err:
        return err
    book.title = payload["title"]
    book.isbn = payload.get("isbn")
    book.price_vnd = payload["price_vnd"]
    book.stock = payload.get("stock", 0)
    book.category_id = payload.get("category_id")
    db.session.commit()
    return jsonify(book.to_dict())


@bp.delete("/<int:bid>")
def delete_book(bid):
    book = _get_book_or_404(bid)
    # review phụ thuộc cứng vào book (slide 9) -> xoá theo
    db.session.execute(db.delete(Review).where(Review.book_id == bid))
    db.session.execute(db.delete(BookAuthor).where(BookAuthor.book_id == bid))
    db.session.delete(book)
    db.session.commit()
    return "", 204


# ---------- N:M nested + pair: /books/<id>/authors ----------

@bp.post("/<int:bid>/authors")
def add_author(bid):
    _get_book_or_404(bid)
    req = request.get_json(silent=True) or {}
    if "author_id" not in req:
        abort(400)
    if db.session.get(Author, req["author_id"]) is None:
        return jsonify(error="author_not_found"), 400
    if db.session.get(BookAuthor, (bid, req["author_id"])):
        return jsonify(error="pair_exists"), 409
    if req.get("role", "co") not in ("lead", "co", "ed"):
        return jsonify(error="bad_role"), 400

    pair = BookAuthor(book_id=bid, author_id=req["author_id"],
                      role=req.get("role", "co"))
    db.session.add(pair)
    db.session.commit()
    return jsonify(bookId=f"book_{bid}", authorId=pair.author_id, role=pair.role), 201


@bp.get("/<int:bid>/authors")
def list_authors(bid):
    _get_book_or_404(bid)
    rows = (db.session.query(Author, BookAuthor.role)
            .join(BookAuthor, Author.id == BookAuthor.author_id)
            .filter(BookAuthor.book_id == bid).all())
    return jsonify([{"id": a.id, "name": a.name, "role": r} for a, r in rows])


@bp.delete("/<int:bid>/authors/<int:aid>")
def remove_author(bid, aid):
    n = BookAuthor.query.filter_by(book_id=bid, author_id=aid).delete()
    db.session.commit()
    if n == 0:
        abort(404)
    return "", 204