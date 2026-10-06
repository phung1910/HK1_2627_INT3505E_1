from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# Dữ liệu giả lập để test API
BOOKS = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin"},
    {"id": 2, "title": "Clean Architecture", "author": "Robert C. Martin"},
    {"id": 3, "title": "1984", "author": "George Orwell"},
    {"id": 4, "title": "Animal Farm", "author": "George Orwell"},
    {"id": 5, "title": "The Pragmatic Programmer", "author": "Andrew Hunt"},
]

DEFAULT_SIZE = 2
MAX_SIZE = 100

@app.get("/books")
def list_books():
    try:
        page = int(request.args.get("page", 1))
        size = int(request.args.get("size", DEFAULT_SIZE))
    except ValueError:
        return jsonify(error="page and size must be int"), 400
    
    page = max(page, 1)
    size = max(min(size, MAX_SIZE), 1)
    
    # Filtering: lọc theo tác giả chính xác (author) hoặc tìm từ khóa trong tiêu đề (q)
    flt = BOOKS
    a = request.args.get("author")
    if a:
        flt = [b for b in flt if b.get("author", "").lower() == a.lower()]
        
    q = request.args.get("q")
    if q:
        flt = [b for b in flt if q.lower() in b.get("title", "").lower()]
        
    # Pagination
    total = len(flt)
    start = (page - 1) * size
    end = start + size
    items = flt[start:end]
    
    # Tính tổng số trang (last)
    last = (total + size - 1) // size
    
    # HATEOAS links
    def u(p): return f"/books?page={p}&size={size}"
    
    links = {"self": {"href": u(page)}}
    if page > 1: 
        links["prev"] = {"href": u(page - 1)}
    if end < total: 
        links["next"] = {"href": u(page + 1)}
        
    links["first"] = {"href": u(1)}
    links["last"] = {"href": u(max(last, 1))}
    
    body = {
        "data": items,
        "pagination": {"page": page, "size": size, "total": total, "total_pages": last},
        "_links": links
    }
    
    resp = make_response(jsonify(body), 200)
    resp.headers["Cache-Control"] = "public, max-age=30"
    
    return resp

if __name__ == "__main__":
    # Bật debug mode để auto-reload code khi có thay đổi
    app.run(debug=True)