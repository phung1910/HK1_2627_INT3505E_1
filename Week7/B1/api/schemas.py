from marshmallow import Schema, fields, validate, validates, ValidationError

# Schema = serialization layer (slide 19). Không truy cập DB, chỉ mô tả
# "dữ liệu nào hợp lệ và được phép trao đổi qua API".


# ─── output: dump model -> JSON ───
class ProductOut(Schema):
    id = fields.Int(dump_only=True)
    sku = fields.Str()
    name = fields.Str()
    description = fields.Str(allow_none=True)
    price_cents = fields.Int()
    qty_in_stock = fields.Int()
    archived = fields.Bool()


# ─── input: tạo mới (POST) ───
class ProductIn(Schema):
    sku = fields.Str(required=True, validate=[
        validate.Length(min=3, max=32),
        validate.Regexp(r"^[A-Z0-9-]+$", error="sku chỉ gồm A-Z, 0-9, dấu -"),
    ])
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    description = fields.Str(load_default=None, allow_none=True)
    price_cents = fields.Int(required=True,
                              validate=validate.Range(min=0, max=10_000_000))
    qty_in_stock = fields.Int(load_default=0, validate=validate.Range(min=0))

    @validates("name")
    def _name_not_blank(self, value, **kwargs):
        # field-level validate= xong rồi vẫn cần rule không tái sử dụng được (slide 32)
        if value.strip() == "":
            raise ValidationError("name trống")


# ─── input: cập nhật một phần (PATCH) — mọi field optional ───
class ProductPatch(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=255))
    description = fields.Str(allow_none=True)
    price_cents = fields.Int(validate=validate.Range(min=0, max=10_000_000))
    qty_in_stock = fields.Int(validate=validate.Range(min=0))


# ─── input: POST /<id>/reserve ───
class ReserveIn(Schema):
    qty = fields.Int(required=True, validate=validate.Range(min=1))


# ─── query string: GET ?page=&size= ───
class ProductQueryArgs(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    size = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))


# ─── output phân trang: {"items": [...], "page", "size", "total"} ───
class ProductPage(Schema):
    items = fields.List(fields.Nested(ProductOut))
    page = fields.Int()
    size = fields.Int()
    total = fields.Int()
