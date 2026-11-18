
W6

B1

Run server

```
cd Week6/B1
../../.venv/Scripts/python.exe app.py
 * Running on http://127.0.0.1:5000
```

## 1. Basic Auth (slide 7-8)

Run GET - thiếu credential

```
GET /api/basic/orders

HTTP/1.1 401 UNAUTHORIZED
WWW-Authenticate: Basic realm="orders"
{ "error": "unauthorized" }
```

Run GET - sai password

```
GET /api/basic/orders
Authorization: Basic (an@vnu.edu.vn:wrongpass)

HTTP/1.1 401 UNAUTHORIZED
{ "error": "unauthorized" }
```

Run GET - đúng credential

```
GET /api/basic/orders
Authorization: Basic (an@vnu.edu.vn:correct horse battery staple)

HTTP/1.1 200 OK
{
  "orders": [
    { "amount": 120000, "id": "o-001", "item": "Clean Code x1", "owner_id": 1 }
  ],
  "principal": { "email": "an@vnu.edu.vn", "id": 1 }
}
```

## 2. API Key (slide 9-12)

Run GET - thiếu key

```
GET /api/apikey/orders

HTTP/1.1 401 UNAUTHORIZED
{ "error": "missing" }
```

Run GET - key sai

```
GET /api/apikey/orders
X-Api-Key: bogus

HTTP/1.1 401 UNAUTHORIZED
{ "error": "invalid" }
```

Run POST - mint key mặc định (scope orders:read)

```
POST /api/keys
{}

HTTP/1.1 201 CREATED
{
  "key": "sk_demo_Y1m0Zx1hh_TpFLnYqAY4aQQja1UIqEJeZw0kbdGq2bc_74c92f81",
  "last4": "2f81",
  "scopes": ["orders:read"]
}
```

Run GET - key hợp lệ, đủ scope

```
GET /api/apikey/orders
X-Api-Key: sk_demo_Y1m0Zx1hh_TpFLnYqAY4aQQja1UIqEJeZw0kbdGq2bc_74c92f81

HTTP/1.1 200 OK
{
  "orders": [
    { "amount": 120000, "id": "o-001", "item": "Clean Code x1", "owner_id": 1 }
  ]
}
```

Run POST - mint key chỉ có scope orders:write

```
POST /api/keys
{"scopes": ["orders:write"]}

HTTP/1.1 201 CREATED
{
  "key": "sk_demo_FPOE6cpsMicQJTN28bn8p5d--w0g7vRgQhwGYhhgKLI_5ed92480",
  "last4": "2480",
  "scopes": ["orders:write"]
}
```

Run GET - key thiếu scope orders:read (403)

```
GET /api/apikey/orders
X-Api-Key: sk_demo_FPOE6cpsMicQJTN28bn8p5d--w0g7vRgQhwGYhhgKLI_5ed92480

HTTP/1.1 403 FORBIDDEN
{ "error": "scope" }
```

## 3. JWT — login / protected / refresh / logout + revocation (slide 15-18)

Run POST - login sai password

```
POST /api/auth/login
{"email":"binh@vnu.edu.vn","password":"wrong"}

HTTP/1.1 401 UNAUTHORIZED
{ "error": "invalid_credentials" }
```

Run POST - login đúng (binh, role=viewer, scope=orders:read)

```
POST /api/auth/login
{"email":"binh@vnu.edu.vn","password":"secret123"}

HTTP/1.1 200 OK
{
  "access": "eyJhbGciOiJIUzI1NiIs...<claims roles=[viewer], scopes=[orders:read]>...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

Run GET - không có token

```
GET /api/jwt/orders

HTTP/1.1 401 UNAUTHORIZED
{ "msg": "Missing Authorization Header" }
```

Run GET - có access token hợp lệ

```
GET /api/jwt/orders
Authorization: Bearer <access của binh>

HTTP/1.1 200 OK
{
  "orders": [
    { "amount": 150000, "id": "o-002", "item": "Refactoring x1", "owner_id": 2 }
  ]
}
```

Run POST - refresh lấy access mới (không cần đăng nhập lại)

```
POST /api/auth/refresh
Authorization: Bearer <refresh của binh>

HTTP/1.1 200 OK
{ "access": "eyJhbGciOiJIUzI1NiIs..." }
```

Run POST - logout (ghi jti vào blocklist in-memory thay Redis)

```
POST /api/auth/logout
Authorization: Bearer <access của binh>

HTTP/1.1 204 NO CONTENT
```

Run GET - dùng lại access token vừa logout → chứng minh blocklist hoạt động

```
GET /api/jwt/orders
Authorization: Bearer <access cũ, đã bị revoke>

HTTP/1.1 401 UNAUTHORIZED
{ "msg": "Token has been revoked" }
```

## 4. RBAC + Scope + Ownership — 3 lớp check trên 1 route (slide 24-26)

`DELETE /api/jwt/orders/<id>` stack: `@jwt_required()` → `@require_roles("admin","manager")` → `@require_scopes("orders:write")` → `@user_owns_resource("id")`.

Seed: `an` = admin (sở hữu order 1), `binh` = viewer (sở hữu order 2), `chau` = manager, không sở hữu order nào.

Run DELETE - binh (role=viewer) xoá order của chính mình → chặn ngay ở lớp role (BFLA, chưa tới lớp ownership)

```
DELETE /api/jwt/orders/2
Authorization: Bearer <access của binh, roles=[viewer]>

HTTP/1.1 403 FORBIDDEN
{ "error": "forbidden", "need_one_of": ["admin", "manager"] }
```

Run DELETE - chau (role=manager, scope orders:write hợp lệ) xoá order 1 của an (không phải chau) → qua được 2 lớp đầu, chặn ở lớp ownership (BOLA, OWASP API1)

```
DELETE /api/jwt/orders/1
Authorization: Bearer <access của chau, roles=[manager]>

HTTP/1.1 403 FORBIDDEN
{ "error": "forbidden" }
```

Run DELETE - an (role=admin) xoá order 2 của binh (không phải an) → admin bypass ownership → thành công

```
DELETE /api/jwt/orders/2
Authorization: Bearer <access của an, roles=[admin]>

HTTP/1.1 204 NO CONTENT
```

Run GET - xác nhận order 2 đã bị xoá (binh login lại, danh sách rỗng)

```
GET /api/jwt/orders
Authorization: Bearer <access mới của binh>

HTTP/1.1 200 OK
{ "orders": [] }
```

## 5. Password hashing — Argon2id (slide 27-28)

Script độc lập, không gắn vào app chính (app chính dùng bcrypt cho Basic Auth + JWT login, đúng code mẫu slide 7/16). Argon2id minh hoạ riêng cho "ưu tiên hệ thống mới".

```
python hash_demo.py

hash: $argon2id$v=19$m=65536,t=3,p=4$knjwxEp/xVAk1gTaSn9eNg$XnROjJulNtyJ7tgZBKerScPhsXIEfJmIP8QYZpr35Js
verify: OK
needs_rehash: False
verify (sai password): MISMATCH (đúng như kỳ vọng)
```
