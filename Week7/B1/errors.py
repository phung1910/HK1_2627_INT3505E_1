from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """Base — mọi lỗi nghiệp vụ (không phải lỗi validate của flask-smorest) kế thừa class này.

    Shape JSON theo đúng hợp đồng Lab 1 (slide 24):
    {"error": "<mã máy đọc>", "detail": "<mô tả cho người>"}.
    """
    status_code = 500
    error = "internal_error"

    def __init__(self, detail="", status=None, error=None):
        super().__init__(detail)
        if error:
            self.error = error
        if status:
            self.status_code = status
        self.detail = detail


class NotFound(ApiError):
    status_code = 404
    error = "not_found"


class Conflict(ApiError):
    status_code = 409
    error = "conflict"


class OutOfStock(ApiError):
    status_code = 409
    error = "out_of_stock"


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def _on_api(err):
        return jsonify({"error": err.error, "detail": err.detail}), err.status_code

    @app.errorhandler(HTTPException)
    def _on_http(err):
        # bắt 404 do Flask tự ném (route không khớp), 405, v.v.
        # Riêng 422 do webargs/flask-smorest abort() kèm theo err.data["messages"]
        # (chi tiết field nào sai, lý do gì) — giữ lại để client biết sửa gì,
        # thay vì chỉ trả câu mô tả chung chung của Werkzeug.
        detail = err.description
        payload = getattr(err, "data", None)
        if payload and "messages" in payload:
            detail = payload["messages"]
        return jsonify({
            "error": err.name.lower().replace(" ", "_"),
            "detail": detail,
        }), err.code

    @app.errorhandler(Exception)
    def _on_err(err):
        app.logger.exception("unhandled")
        return jsonify({"error": "internal_error", "detail": "unexpected error"}), 500
