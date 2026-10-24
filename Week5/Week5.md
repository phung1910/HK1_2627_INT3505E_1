
W5

B1

Run server

```
cd Week5/B1
../../.venv/Scripts/python.exe app.py
 * Running on http://127.0.0.1:5000
```

Run POST (create book)

```
POST /api/v1/books
{"title":"Clean Code","price_vnd":120000,"stock":5}

HTTP/1.1 201 CREATED
{
  "id": "book_1",
  "title": "Clean Code",
  "isbn": null,
  "category": null,
  "authors": [],
  "price": { "amount": 120000, "currency": "VND" },
  "inStock": true
}
```

Run POST validation error (missing price_vnd)

```
POST /api/v1/books
{"title":"Bad Book"}

HTTP/1.1 400 BAD REQUEST
{
  "error": "validation_failed",
  "field": [],
  "message": "'price_vnd' is a required property"
}
```

Run GET 404 (unknown id)

```
GET /api/v1/books/9999

HTTP/1.1 404 NOT FOUND
{ "error": "not_found" }
```

Run GET - offset/limit pagination

```
GET /api/v1/books?offset=0&limit=5

{
  "data": [
    { "id": "book_1",  "title": "Clean Code" },
    { "id": "book_2",  "title": "The Pragmatic Programmer" },
    { "id": "book_3",  "title": "Refactoring" },
    { "id": "book_4",  "title": "Design Patterns" },
    { "id": "book_5",  "title": "Domain-Driven Design" }
  ],
  "pagination": { "offset": 0, "limit": 5, "total": 13, "has_next": true }
}
```

```
GET /api/v1/books?offset=5&limit=5

{
  "data": [
    { "id": "book_6",  "title": "Clean Architecture" },
    { "id": "book_7",  "title": "Effective Java" },
    { "id": "book_8",  "title": "You Don't Know JS" },
    { "id": "book_9",  "title": "Introduction to Algorithms" },
    { "id": "book_10", "title": "The Mythical Man-Month" }
  ],
  "pagination": { "offset": 5, "limit": 5, "total": 13, "has_next": true }
}
```

Run GET - cursor pagination (keyset by id)

```
GET /api/v1/books/cursor?limit=5

{
  "data": [
    { "id": "book_1", "title": "Clean Code" },
    { "id": "book_2", "title": "The Pragmatic Programmer" },
    { "id": "book_3", "title": "Refactoring" },
    { "id": "book_4", "title": "Design Patterns" },
    { "id": "book_5", "title": "Domain-Driven Design" }
  ],
  "page_info": { "next_cursor": 5, "has_more": true }
}
```

```
GET /api/v1/books/cursor?limit=5&after_id=5

{
  "data": [
    { "id": "book_6",  "title": "Clean Architecture" },
    { "id": "book_7",  "title": "Effective Java" },
    { "id": "book_8",  "title": "You Don't Know JS" },
    { "id": "book_9",  "title": "Introduction to Algorithms" },
    { "id": "book_10", "title": "The Mythical Man-Month" }
  ],
  "page_info": { "next_cursor": 10, "has_more": true }
}
```

Run GET - composite seek cursor (sorted by price_vnd desc, tie-break id)

```
GET /api/v1/books/seek?limit=5

{
  "data": [
    { "id": "book_7",  "title": "Effective Java",                     "price": 300000 },
    { "id": "book_13", "title": "Database Internals",                 "price": 260000 },
    { "id": "book_5",  "title": "Domain-Driven Design",                "price": 250000 },
    { "id": "book_9",  "title": "Introduction to Algorithms",          "price": 220000 },
    { "id": "book_12", "title": "Working Effectively with Legacy Code","price": 210000 }
  ],
  "page_info": { "next_cursor": "eyJ2IjogMjEwMDAwLCAiaSI6IDEyfQ", "has_more": true }
}
```

```
GET /api/v1/books/seek?limit=5&cursor=eyJ2IjogMjEwMDAwLCAiaSI6IDEyfQ

{
  "data": [
    { "id": "book_4",  "title": "Design Patterns", "price": 200000 },
    { "id": "book_11", "title": "Code Complete",    "price": 175000 },
    { "id": "book_3",  "title": "Refactoring",      "price": 150000 },
    { "id": "book_6",  "title": "Clean Architecture","price": 120000 },
    { "id": "book_1",  "title": "Clean Code",       "price": 120000 }
  ],
  "page_info": { "next_cursor": "eyJ2IjogMTIwMDAwLCAiaSI6IDF9", "has_more": true }
}
```

Run GET - seek with invalid cursor (400)

```
GET /api/v1/books/seek?cursor=not-valid

HTTP/1.1 400 BAD REQUEST
{ "error": "invalid_cursor" }
```

Run GET - page number + Link header

```
GET /api/v1/books/page?page=2&per_page=5

HTTP/1.1 200 OK
Link: </api/v1/books/page?page=1&per_page=5>; rel="first",
      </api/v1/books/page?page=1&per_page=5>; rel="prev",
      </api/v1/books/page?page=3&per_page=5>; rel="next",
      </api/v1/books/page?page=3&per_page=5>; rel="last"

{
  "data": [
    { "id": "book_6",  "title": "Clean Architecture" },
    { "id": "book_7",  "title": "Effective Java" },
    { "id": "book_8",  "title": "You Don't Know JS" },
    { "id": "book_9",  "title": "Introduction to Algorithms" },
    { "id": "book_10", "title": "The Mythical Man-Month" }
  ]
}
```

B1 - Lab 2

`GET /api/v1/books/search` kết hợp: filter (category) + sort whitelist (parse_sort) + composite cursor (apply_cursor) + field selection (fields). Helper tách riêng: parse_sort, apply_cursor, build_page.

Run GET - default sort (-id), không filter

```
GET /api/v1/books/search?limit=3

{
  "data": [
    { "id": "book_13", "title": "Clean Code",       "price": 120000, "category": null },
    { "id": "book_12", "title": "Database Internals","price": 260000, "category": null },
    { "id": "book_11", "title": "Working Effectively with Legacy Code", "price": 210000, "category": {"id":1,"slug":"tech"} }
  ],
  "page": { "next_cursor": "eyJzIjogIi1pZCIsICJ2IjogMTEsICJpIjogMTF9", "has_more": true }
}
```

Run GET - sort=price (asc, whitelist qua SORT_COLUMNS)

```
GET /api/v1/books/search?sort=price&limit=3

{
  "data": [
    { "id": "book_7", "title": "You Don't Know JS",        "price": 80000 },
    { "id": "book_1", "title": "The Pragmatic Programmer",  "price": 90000 },
    { "id": "book_9", "title": "The Mythical Man-Month",    "price": 95000 }
  ],
  "page": { "next_cursor": "eyJzIjogInByaWNlIiwgInYiOiA5NTAwMCwgImkiOiA5fQ", "has_more": true }
}
```

Run GET - category filter + sort=-price + field selection

```
GET /api/v1/books/search?category=1&sort=-price&fields=id,title,price&limit=5

{
  "data": [
    { "id": "book_8",  "title": "Introduction to Algorithms", "price": {"amount":220000,"currency":"VND"} },
    { "id": "book_11", "title": "Working Effectively with Legacy Code", "price": {"amount":210000,"currency":"VND"} },
    { "id": "book_2",  "title": "Refactoring", "price": {"amount":150000,"currency":"VND"} },
    { "id": "book_5",  "title": "Clean Architecture", "price": {"amount":120000,"currency":"VND"} },
    { "id": "book_1",  "title": "The Pragmatic Programmer", "price": {"amount":90000,"currency":"VND"} }
  ],
  "page": { "next_cursor": null, "has_more": false }
}
```

Run GET - bad sort key (whitelist rejects, 400)

```
GET /api/v1/books/search?sort=foo

HTTP/1.1 400 BAD REQUEST
{ "error": "bad_sort" }
```

Run GET - cursor paging tiếp tục cùng sort (tie-break by id khi price trùng 120000: book_5 trước book_13)

```
GET /api/v1/books/search?sort=price&limit=3&cursor=eyJzIjogInByaWNlIiwgInYiOiA5NTAwMCwgImkiOiA5fQ

{
  "data": [
    { "id": "book_5",  "title": "Clean Architecture", "price": 120000 },
    { "id": "book_13", "title": "Clean Code",         "price": 120000 },
    { "id": "book_2",  "title": "Refactoring",         "price": 150000 }
  ],
  "page": { "next_cursor": "eyJzIjogInByaWNlIiwgInYiOiAxNTAwMDAsICJpIjogMn0", "has_more": true }
}
```

Run GET - cursor dùng với sort khác lúc tạo cursor (bị chặn, 400 sort_changed)

```
GET /api/v1/books/search?sort=-id&limit=3&cursor=eyJzIjogInByaWNlIiwgInYiOiA5NTAwMCwgImkiOiA5fQ

HTTP/1.1 400 BAD REQUEST
{ "error": "sort_changed" }
```

Run GET - field selection chỉ id, title

```
GET /api/v1/books/search?limit=2&fields=id,title

{
  "data": [
    { "id": "book_13", "title": "Clean Code" },
    { "id": "book_12", "title": "Database Internals" }
  ],
  "page": { "next_cursor": "eyJzIjogIi1pZCIsICJ2IjogMTIsICJpIjogMTJ9", "has_more": true }
}
```
