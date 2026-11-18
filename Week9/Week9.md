# W9 — API Versioning & Lifecycle

## B1 — Lab 1: URI Path Versioning với Flask Blueprint

### Run server

```powershell
cd Week9/B1
../../.venv/Scripts/python.exe app.py
```

### Test 2 version cùng user 1

```powershell
curl http://127.0.0.1:5000/api/v1/users/1
```
```json
{
  "id": 1,
  "full_name": "Văn Nguyễn",
  "email": "van.nguyen@example.com"
}
```

```powershell
curl http://127.0.0.1:5000/api/v2/users/1
```
```json
{
  "id": 1,
  "first_name": "Văn",
  "last_name": "Nguyễn",
  "email": "van.nguyen@example.com"
}
```

```powershell
curl http://127.0.0.1:5000/api/v1/users/999
```
```json
{
  "error": "nf"
}
```
