from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import Product
from errors import NotFound, Conflict, OutOfStock
from api.schemas import (
    ProductOut, ProductIn, ProductPatch, ReserveIn,
    ProductQueryArgs, ProductPage,
)

# Resource = transport layer (slide 19): nhận request, gọi DB qua session,
# trả output qua schema. blp biết extension (db) nhưng CHƯA gắn vào app —
# app.py / factory.py sẽ register_blueprint (slide 16).
blp = Blueprint(
    "products", __name__, url_prefix="/api/v1/products",
    description="CRUD sản phẩm — demo Code-First với flask-smorest (Buổi 7)",
)


def _get_active_or_404(id):
    product = db.session.get(Product, id)
    if product is None or product.archived:
        raise NotFound(detail=f"product {id} not found")
    return product


@blp.route("")
class ProductList(MethodView):
    """GET /api/v1/products, POST /api/v1/products"""

    @blp.arguments(ProductQueryArgs, location="query")
    @blp.response(200, ProductPage)
    def get(self, args):
        page, size = args["page"], args["size"]
        base = db.select(Product).where(Product.archived.is_(False))
        rows = db.session.execute(
            base.order_by(Product.id)
            .offset((page - 1) * size).limit(size)
        ).scalars().all()
        total = db.session.scalar(
            db.select(db.func.count()).select_from(Product)
            .where(Product.archived.is_(False))
        )
        return {"items": rows, "page": page, "size": size, "total": total}

    @blp.arguments(ProductIn)
    @blp.response(201, ProductOut)
    def post(self, data):
        product = Product(**data)
        db.session.add(product)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise Conflict(detail="sku already exists")
        return product


@blp.route("/<int:id>")
class ProductDetail(MethodView):
    """GET/PATCH/DELETE /api/v1/products/<id>"""

    @blp.response(200, ProductOut)
    def get(self, id):
        return _get_active_or_404(id)

    @blp.arguments(ProductPatch)
    @blp.response(200, ProductOut)
    def patch(self, data, id):
        product = _get_active_or_404(id)
        for key, value in data.items():
            setattr(product, key, value)
        db.session.commit()
        return product

    @blp.response(204)
    def delete(self, id):
        # soft-delete: không xoá hàng, chỉ đánh dấu archived (slide 24)
        product = _get_active_or_404(id)
        product.archived = True
        db.session.commit()


@blp.route("/<int:id>/reserve")
class ProductReserve(MethodView):
    """POST /api/v1/products/<id>/reserve"""

    @blp.arguments(ReserveIn)
    @blp.response(200, ProductOut)
    def post(self, data, id):
        product = _get_active_or_404(id)
        if product.qty_in_stock < data["qty"]:
            raise OutOfStock(detail=f"only {product.qty_in_stock} left")
        product.qty_in_stock -= data["qty"]
        db.session.commit()
        return product
