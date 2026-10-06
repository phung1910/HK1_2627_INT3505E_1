from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# ==============================================================
# PHẦN 1: BÀI TẬP ERROR HANDLER VÀ PROBLEM+JSON (Route: /users)
# ==============================================================
ERROR_BASE = "https://api.example.com/probs"

class ApiProblem(Exception):
    def __init__(self, status, title, detail=None, type_path=None, **extra):
        super().__init__()
        self.status = status
        self.title = title
        self.detail = detail
        self.type = f"{ERROR_BASE}/{type_path}" if type_path else "about:blank"
        self.extra = extra

@app.errorhandler(ApiProblem)
def handle_api_problem(error):
    body = {
        "type": error.type,
        "title": error.title,
        "status": error.status,
        "instance": request.path,
        "trace_id": str(uuid.uuid4())[:8]
    }
    if error.detail:
        body["detail"] = error.detail
    body.update(error.extra)

    resp = jsonify(body)
    resp.status_code = error.status
    resp.headers["Content-Type"] = "application/problem+json"
    return resp

users_db = {
    1: {"id": 1, "name": "Admin"},
    42: {"id": 42, "name": "Người dùng 42"}
}

@app.route("/users/", methods=["GET"])
def get_user(user_id):
    user = users_db.get(user_id)
    if not user:
        raise ApiProblem(
            status=404,
            title="User not found",
            type_path="user-not-found",
            resource_id=user_id
        )
    return jsonify(user)

# ==============================================================
# PHẦN 2: BÀI TẬP FILTERING, SORTING, PAGINATION (Route: /products)
# ==============================================================
products_db = [
    {"id": 1, "name": "Laptop", "category": "electronics", "price": 1000, "status": "active", "created_at": "2026-01-01"},
    {"id": 2, "name": "Mouse", "category": "electronics", "price": 50, "status": "active", "created_at": "2026-01-02"},
    {"id": 3, "name": "Keyboard", "category": "electronics", "price": 100, "status": "inactive", "created_at": "2026-01-03"},
    {"id": 4, "name": "Monitor", "category": "electronics", "price": 300, "status": "active", "created_at": "2026-01-04"},
    {"id": 5, "name": "Desk", "category": "furniture", "price": 200, "status": "active", "created_at": "2026-01-05"},
]

@app.route("/products", methods=["GET"])
def get_products():
    result = products_db.copy()
    
    category = request.args.get("category")
    status = request.args.get("status")
    price_min = request.args.get("price_min", type=float)

    if category:
        result = [p for p in result if p["category"] == category]
    if status:
        result = [p for p in result if p["status"] == status]
    if price_min is not None:
        result = [p for p in result if p["price"] >= price_min]

    sort_by = request.args.get("sort")
    if sort_by:
        reverse = False
        if sort_by.startswith("-"):
            reverse = True
            sort_by = sort_by[1:]
        if result and sort_by in result[0]:
            result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    fields = request.args.get("fields")
    if fields:
        field_list = fields.split(",")
        result = [{k: v for k, v in p.items() if k in field_list} for p in result]

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 2, type=int)
    if per_page > 100:
        per_page = 100

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_result = result[start_index:end_index]

    return jsonify({
        "data": paginated_result,
        "meta": {
            "page": page,
            "per_page": per_page,
            "total_records": len(result)
        }
    })

if __name__ == '__main__':
    app.run(debug=True)