from flask import Flask
from flask_smorest import Api

app = Flask(__name__)

# --- CẤU HÌNH OPENAPI & SWAGGER UI ---
app.config["API_TITLE"] = "My Product API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

# Khởi tạo extension Api của flask-smorest
api = Api(app)

# --- ĐĂNG KÝ BLUEPRINT ---
# Import Blueprint từ file resource sản phẩm của bạn (ví dụ: api/products.py)
from api.products import blp as ProductBlueprint
api.register_blueprint(ProductBlueprint)

if __name__ == "__main__":
    app.run(debug=True)