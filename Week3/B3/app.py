from flask import Flask, request, jsonify
import base64
import uuid

# 1. Khởi tạo ứng dụng Flask
app = Flask(__name__)

# ==============================================================
# PHẦN 1: ERROR HANDLER (Trả về lỗi chuẩn problem+json khi cursor hỏng)
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

# ==============================================================
# PHẦN 2: BÀI TẬP CURSOR PAGINATION (Route: /orders)
# ==============================================================
orders_db = [
    {"id": 1, "customer_id": 101, "status": "paid", "total": 250.0, "created_at": "2026-10-01"},
    {"id": 2, "customer_id": 102, "status": "pending", "total": 100.0, "created_at": "2026-10-02"},
    {"id": 3, "customer_id": 101, "status": "paid", "total": 300.0, "created_at": "2026-10-03"},
    {"id": 4, "customer_id": 103, "status": "cancelled", "total": 50.0, "created_at": "2026-10-04"},
    {"id": 5, "customer_id": 104, "status": "paid", "total": 450.0, "created_at": "2026-10-05"},
    {"id": 6, "customer_id": 102, "status": "paid", "total": 120.0, "created_at": "2026-10-06"},
]

@app.route("/orders", methods=["GET"])
def get_orders():
    result = orders_db.copy()

    # 1. Filter: status, customer_id
    status = request.args.get("status")
    customer_id = request.args.get("customer_id", type=int)
    
    if status:
        result = [o for o in result if o["status"] == status]
    if customer_id:
        result = [o for o in result if o["customer_id"] == customer_id]

    # 2. Sort
    sort_by = request.args.get("sort")
    if sort_by:
        reverse = sort_by.startswith("-")
        key = sort_by.lstrip("-")
        if result and key in result[0]:
            result = sorted(result, key=lambda x: x[key], reverse=reverse)

    # 3. Cursor Pagination
    limit = request.args.get("limit", 2, type=int)
    cursor = request.args.get("cursor")

    if cursor:
        try:
            # Giải mã cursor từ base64
            decoded_bytes = base64.b64decode(cursor)
            last_id = int(decoded_bytes.decode('utf-8'))
            result = [o for o in result if o["id"] > last_id]
        except Exception:
            # Nếu cursor nhập vào bị hỏng/không hợp lệ -> văng lỗi 400
            raise ApiProblem(
                status=400,
                title="Bad Request",
                detail="Invalid cursor format. Cursor must be a valid base64 string.",
                type_path="invalid-cursor"
            )

    paginated_result = result[:limit]

    # Tạo next_cursor
    next_cursor = None
    if len(result) > limit:
        last_item = paginated_result[-1]
        cursor_str = str(last_item["id"]).encode('utf-8')
        next_cursor = base64.b64encode(cursor_str).decode('utf-8')

    # 4. Sparse fieldsets
    fields = request.args.get("fields")
    if fields:
        field_list = fields.split(",")
        paginated_result = [{k: v for k, v in o.items() if k in field_list} for o in paginated_result]

    return jsonify({
        "data": paginated_result,
        "meta": {
            "limit": limit,
            "next_cursor": next_cursor
        }
    })

if __name__ == '__main__':
    app.run(debug=True)