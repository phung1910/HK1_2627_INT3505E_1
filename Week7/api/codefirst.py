from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from .schemas import ProductSchema, ProductInSchema
from .models import Product
from ..extensions import db

# Khởi tạo Blueprint với tiền tố URL là /products
blp = Blueprint("products", __name__, url_prefix="/products")

class ProductList(MethodView):
    
    @blp.arguments(ProductInSchema)   # Tự động validate dữ liệu gửi lên ở POST body
    @blp.response(201, ProductSchema) # Tự động serialize dữ liệu trả về với mã HTTP 201
    def post(self, data):
        """Tạo mới một sản phẩm"""
        p = Product(**data)
        db.session.add(p)
        db.session.commit()
        return p

    @blp.response(200, ProductSchema(many=True)) # Trả về danh sách sản phẩm (nhiều bản ghi)
    def get(self):
        """Lấy danh sách tất cả sản phẩm"""
        return db.session.execute(db.select(Product)).scalars().all()

# Đăng ký View vào Blueprint
blp.add_url_rule("", view_func=ProductList.as_view("product_list"))