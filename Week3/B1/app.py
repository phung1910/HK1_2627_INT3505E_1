from flask import Flask, request, jsonify

app = Flask(__name__)

# Mock database lưu trữ các bài viết (posts)
posts = [
    {"id": 1, "title": "Giới thiệu HTTP Methods", "content": "GET, POST, PUT, DELETE..."},
    {"id": 2, "title": "Status code là gì?", "content": "1xx đến 5xx..."}
]

# 1. API lấy danh sách bài viết (GET)
@app.route('/posts', methods=['GET'])
def get_posts():
    # Trả về 200 OK mặc định cho GET có dữ liệu[cite: 3]
    return jsonify({
        "data": posts,
        "total": len(posts)
    }), 200 

# 2. API tạo bài viết mới (POST)
@app.route('/posts', methods=['POST'])
def create_post():
    body = request.get_json()

    # Validate dữ liệu đầu vào. Nếu thiếu required field -> 400 Bad Request[cite: 3]
    if not body or 'title' not in body or 'content' not in body:
        # Áp dụng thiết kế error response: RFC 7807 / 9457[cite: 3]
        error_response = {
            "type": "https://api.blog.example/probs/missing-fields",
            "title": "Bad Request",
            "detail": "Thiếu trường 'title' hoặc 'content' trong request body.",
            "status": 400,
            "instance": request.path
        }
        return jsonify(error_response), 400 

    # Tạo resource mới
    new_post = {
        "id": len(posts) + 1,
        "title": body['title'],
        "content": body['content'],
        "tags": body.get('tags', []) # Mở rộng thêm tags nếu có
    }
    posts.append(new_post)

    # Trả về 201 Created khi tạo resource mới thành công[cite: 3]
    return jsonify(new_post), 201 

if __name__ == '__main__':
    app.run(debug=True)