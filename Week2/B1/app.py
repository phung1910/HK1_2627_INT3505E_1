# app.py — bài 1: GET /books, POST /books
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# Khởi tạo danh sách rỗng ban đầu
BOOKS = []
_next_id = 1

# --- GET /books — trả danh sách
@app.get("/books")
def list_books():
    return jsonify({
        "data": BOOKS,
        "total": len(BOOKS)
    }), 200

# --- POST /books — tạo mới
@app.post("/books")
def create_book():
    global _next_id
    
    # Check nếu request không phải là JSON (Thiếu Content-Type)
    if not request.is_json:
        return jsonify(error="expected JSON"), 415
    
    p = request.get_json(silent=True) or {}
    t = (p.get("title") or "").strip()
    a = (p.get("author") or "").strip()
    
    # Check thiếu field title hoặc author
    if not t or not a:
        return jsonify(error="title and author required"), 422
    
    # Tạo book mới và lưu vào mảng
    book = {"id": _next_id, "title": t, "author": a}
    BOOKS.append(book)
    _next_id += 1
    
    # Trả về response thành công
    resp = make_response(jsonify(book), 201)
    resp.headers["Location"] = f"/books/{book['id']}"
    return resp