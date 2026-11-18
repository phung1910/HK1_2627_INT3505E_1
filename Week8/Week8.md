# W8 — API Testing và Quality Assurance

## Lab 1 - pytest

### Run pytest

```powershell
cd Week8/lab08-starter
.\.venv\Scripts\python.exe -m pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.13.15, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\ROG\flask_api\HK1_2627_INT3505E_1\Week8\lab08-starter\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ROG\flask_api\HK1_2627_INT3505E_1\Week8\lab08-starter
configfile: pytest.ini
testpaths: tests
plugins: locust-2.47.0
collecting ... collected 7 items

tests/test_lab01.py::test_list_books_empty_db_returns_empty_array PASSED [ 14%]
tests/test_lab01.py::test_get_unknown_book_returns_404_not_found PASSED  [ 28%]
tests/test_lab01.py::test_create_book_missing_title_returns_400 PASSED   [ 42%]
tests/test_lab01.py::test_deleted_book_is_gone PASSED                    [ 57%]
tests/test_lab01.py::test_response_extra_field_blocked PASSED            [ 71%]
tests/test_smoke.py::test_health PASSED                                  [ 85%]
tests/test_smoke.py::test_book_can_be_created PASSED                     [100%]

============================== 7 passed in 0.86s ==============================
```

---

## Lab 2 - Spectral lint OpenAPI

### Run spectral lint (trước khi sửa)

```powershell
spectral lint openapi.yaml --ruleset .spectral.yml
```

```
c:/Users/ROG/flask_api/HK1_2627_INT3505E_1/Week8/lab08-starter/openapi.yaml
  2:6   warning  info-contact             Info object must have "contact" object.                                    info
  12:9  warning  operation-description    Operation "description" must be present and non-empty string.              paths./health.get
  12:9  warning  operation-tags           Operation must have non-empty "tags" array.                                paths./health.get
  24:9  warning  operation-description    Operation "description" must be present and non-empty string.              paths./books.get
  24:9  warning  operation-operationId    Operation must have "operationId".                                         paths./books.get
  24:9  warning  operation-tags           Operation must have non-empty "tags" array.                                paths./books.get
 44:10  warning  operation-description    Operation "description" must be present and non-empty string.              paths./books.post
 44:10  warning  operation-tags           Operation must have non-empty "tags" array.                                paths./books.post
  65:9  warning  operation-description    Operation "description" must be present and non-empty string.              paths./books/{id}.get
  65:9  warning  operation-tags           Operation must have non-empty "tags" array.                                paths./books/{id}.get
  74:9  warning  operation-description    Operation "description" must be present and non-empty string.              paths./books/{id}.put
  74:9  warning  operation-tags           Operation must have non-empty "tags" array.                                paths./books/{id}.put
 89:12  warning  operation-description    Operation "description" must be present and non-empty string.              paths./books/{id}.delete
 89:12  warning  operation-tags           Operation must have non-empty "tags" array.                                paths./books/{id}.delete
 95:19    error  no-204-response-content  HTTP 204 No Content responses must not declare a response body (content).  paths./books/{id}.delete.responses[204].content

✖ 15 problems (1 error, 14 warnings, 0 infos, 0 hints)
```

### Các lỗi đã sửa trong `openapi.yaml`
1. Thêm `operationId: listBooks` cho `GET /books`.
2. Xóa `content` body khỏi response `204` của `DELETE /books/{id}`.
3. Sửa `components.schemas.Book.properties.year` từ `type: string` thành `type: integer` (khớp với `models.py` và `BookInput`).
4. Bổ sung `info.contact`, `tags`, và `description` cho các operation để đạt 0 warning theo `spectral:oas`.

### Custom rule trong `.spectral.yml`
- `response-200-schema-has-properties`: Bắt các endpoint trả về HTTP `200` (`application/json`) có schema dạng `object` (hoặc `array` chứa `items` dạng `object`) nhưng khai báo `properties` rỗng (`0` trường).
- `no-204-response-content`: Bắt các response `204 No Content` khai báo nhầm `content` body.

### Câu hỏi thảo luận: Nếu spec hợp lệ (Spectral pass) nhưng code Flask trả sai field — test nào bắt được?
- **Spectral** chỉ kiểm tra *tĩnh* trên file `openapi.yaml`, không chạy code Flask nên không bắt được lệch giữa implementation và spec.
- Cần dùng **Integration / Contract test** (tầng ②/③) bằng `pytest` + `flask.test_client()` kết hợp `jsonschema.validate(response.get_json(), schema)` (như `test_response_extra_field_blocked` trong `tests/test_lab01.py` đọc schema từ `openapi.yaml` với `additionalProperties: false` và `required`) để phát hiện ngay khi backend trả thiếu field, sai kiểu dữ liệu hoặc lộ field lạ.

### Run spectral lint (sau khi sửa)

```powershell
spectral lint openapi.yaml --ruleset .spectral.yml
```

```
No results with a severity of 'error' found!
```

(Log được lưu tại `reports/spectral-lint.log`.)

---

## Lab 3 - Postman/Newman

### Run newman

Chạy script tự động khởi động Flask API, đợi `/health`, chạy Newman và xuất báo cáo JUnit XML (`reports/junit.xml`):

```powershell
cd Week8/lab08-starter
powershell -ExecutionPolicy Bypass -File .\run_newman.ps1
```

Hoặc chạy thủ công khi server Flask đang chạy ở cổng 5000:

```powershell
newman run books-api.postman_collection.json -e postman/local.postman_environment.json -r "cli,junit" --reporter-junit-export reports/junit.xml
```

```
newman

Books API — Lab08

□ books
└ GET /books — initial list [200 OK] (2/2 assertions passed)
└ POST /books — create [201 CREATED] (2/2 assertions passed, lưu book_id)
└ GET /books/{id} — read [200 OK] (2/2 assertions passed)
└ PUT /books/{id} — replace [200 OK] (2/2 assertions passed)
└ DELETE /books/{id} — delete [204 NO CONTENT] (2/2 assertions passed)

□ error-cases
└ POST /books — missing title [400 BAD REQUEST] (2/2 assertions passed)
└ GET /books/9999 — not found [404 NOT FOUND] (2/2 assertions passed)

iterations: 1 | requests: 7 (0 failed) | test-scripts: 7 (0 failed) | assertions: 14 (0 failed)
total run duration: 633ms
```

---

## Lab 4 - Locust

Run locust
