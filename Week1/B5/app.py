from flask import Flask, jsonify

app = Flask(__name__)

# Giả lập DB với dữ liệu mẫu
ORDERS = {
    "1": {"id": "1", "item": "Laptop", "status": "pending"},    # Hợp lệ để xóa
    "2": {"id": "2", "item": "Mouse", "status": "shipped"},     # Lỗi 409 (đã giao)
    "3": {"id": "3", "item": "Keyboard", "status": "delivered"} # Lỗi 409 (đã giao)
}

@app.route("/orders/", methods=["DELETE"])
def delete_order(order_id):
    order = ORDERS.get(order_id)
    
    # 404 - không tìm thấy
    if order is None:
        return {"error": "not found"}, 404
        
    # 409 - business rule
    if order["status"] in ("shipped", "delivered"):
        return {"error": "cannot delete"}, 409
        
    ORDERS.pop(order_id, None)
    
    # 204 - success, no body
    return "", 204

if __name__ == "__main__":
    app.run(debug=True, port=5000)