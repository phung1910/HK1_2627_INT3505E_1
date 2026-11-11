
W7 — Phần Code-First (flask-smorest)

B1 — Lab 1: Product API CRUD, xây bằng flask-smorest (MethodView + @blp.arguments/@blp.response)

Run server

```
cd Week7/B1
../../.venv/Scripts/python.exe wsgi.py
 * Running on http://127.0.0.1:5000
 * Swagger UI tự sinh tại /docs, spec thô tại /openapi.json
```

## 1. GET /api/v1/products — rỗng lúc khởi tạo

```
GET /api/v1/products

HTTP/1.1 200 OK
{ "items": [], "page": 1, "size": 20, "total": 0 }
```

## 2. POST /api/v1/products — tạo hợp lệ

```
POST /api/v1/products
{"sku":"SKU-001","name":"Keyboard","price_cents":500000,"qty_in_stock":10}

HTTP/1.1 201 CREATED
{
  "id": 1, "sku": "SKU-001", "name": "Keyboard",
  "description": null, "price_cents": 500000,
  "qty_in_stock": 10, "archived": false
}
```

## 3. POST — thiếu field required → 422 tự động từ flask-smorest/webargs

flask-smorest tự validate body bằng `@blp.arguments(ProductIn)` trước khi vào hàm `post()`; không cần code `if` thủ công.

```
POST /api/v1/products
{"name":"No SKU"}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{
  "error": "unprocessable_entity",
  "detail": {
    "json": {
      "sku": ["Missing data for required field."],
      "price_cents": ["Missing data for required field."]
    }
  }
}
```

## 4. POST — sai regex / custom `@validates` / range

```
POST /api/v1/products
{"sku":"bad-sku","name":"X","price_cents":1000}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{ "error": "unprocessable_entity",
  "detail": { "json": { "sku": ["sku chỉ gồm A-Z, 0-9, dấu -"] } } }
```

```
POST /api/v1/products
{"sku":"SKU-002","name":"   ","price_cents":1000}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{ "error": "unprocessable_entity",
  "detail": { "json": { "name": ["name trống"] } } }
```

```
POST /api/v1/products
{"sku":"SKU-003","name":"Mouse","price_cents":-5}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{ "error": "unprocessable_entity",
  "detail": { "json": { "price_cents": ["Must be greater than or equal to 0 and less than or equal to 10000000."] } } }
```

## 5. POST — sku trùng → 409 (business error tự viết, không phải flask-smorest)

```
POST /api/v1/products
{"sku":"SKU-001","name":"Keyboard 2","price_cents":100000}

HTTP/1.1 409 CONFLICT
{ "error": "conflict", "detail": "sku already exists" }
```

## 6. GET /api/v1/products/<id>

```
GET /api/v1/products/1
HTTP/1.1 200 OK
{ "id": 1, "sku": "SKU-001", "name": "Keyboard", ... }

GET /api/v1/products/999
HTTP/1.1 404 NOT FOUND
{ "error": "not_found", "detail": "product 999 not found" }
```

## 7. PATCH /api/v1/products/<id> — cập nhật một phần

```
PATCH /api/v1/products/1
{"name":"Mechanical Keyboard","price_cents":550000}

HTTP/1.1 200 OK
{ "id": 1, "name": "Mechanical Keyboard", "price_cents": 550000, ... }
```

```
PATCH /api/v1/products/1
{"price_cents":-1}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{ "error": "unprocessable_entity",
  "detail": { "json": { "price_cents": ["Must be greater than or equal to 0 and less than or equal to 10000000."] } } }
```

## 8. POST /api/v1/products/<id>/reserve

```
POST /api/v1/products/1/reserve
{"qty":3}

HTTP/1.1 200 OK
{ "id": 1, "qty_in_stock": 7, ... }   # 10 - 3
```

```
POST /api/v1/products/1/reserve
{"qty":100}

HTTP/1.1 409 CONFLICT
{ "error": "out_of_stock", "detail": "only 7 left" }
```

```
POST /api/v1/products/1/reserve
{"qty":0}

HTTP/1.1 422 UNPROCESSABLE ENTITY
{ "error": "unprocessable_entity",
  "detail": { "json": { "qty": ["Must be greater than or equal to 1."] } } }
```

## 9. DELETE /api/v1/products/<id> — soft delete

```
POST /api/v1/products   {"sku":"SKU-004","name":"Monitor","price_cents":3000000,"qty_in_stock":5}
HTTP/1.1 201 CREATED    # id=2

DELETE /api/v1/products/1
HTTP/1.1 204 NO CONTENT

GET /api/v1/products/1          → 404 not_found   (archived bị loại trừ khỏi get)
GET /api/v1/products?page=1&size=20
HTTP/1.1 200 OK
{ "items": [ { "id": 2, "sku": "SKU-004", "name": "Monitor", ... } ],
  "page": 1, "size": 20, "total": 1 }   # chỉ còn sản phẩm chưa archive
```

## 10. Query string cũng qua schema — page=0 → 422

```
GET /api/v1/products?page=0

HTTP/1.1 422 UNPROCESSABLE ENTITY
{ "error": "unprocessable_entity",
  "detail": { "query": { "page": ["Must be greater than or equal to 1."] } } }
```

## 11. OpenAPI tự sinh — không viết tay 1 dòng YAML nào

```
GET /docs          → 200 OK   (Swagger UI render từ spec bên dưới)
GET /openapi.json  → 200 OK, openapi: "3.0.3"

paths tự sinh:
  /api/v1/products              [get, post]
  /api/v1/products/{id}         [get, patch, delete]
  /api/v1/products/{id}/reserve [post]

components.schemas tự sinh:
  Error, PaginationMetadata, ProductOut, ProductPage,
  ProductIn, ProductPatch, ReserveIn
```

---

Ghi chú: toàn bộ log trên được chạy lại **từ đầu** (xoá `instance/products.db`, viết lại từng file, khởi động server mới) để xác nhận không có bước nào phụ thuộc trạng thái cũ — kết quả giống hệt lần chạy trước, kể cả thứ tự id (1 → Keyboard, 2 → Monitor).
