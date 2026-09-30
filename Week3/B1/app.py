from flask import Flask, request, jsonify

app = Flask(__name__)

# Dữ liệu giả lập (Mock Database) thay cho CSDL thật
posts_db = []

@app.route('/api/v1/posts', methods=['GET'])
def get_posts():
    return jsonify({"status": "success", "data": posts_db}), 200

@app.route('/api/v1/posts', methods=['POST'])
def create_post():
    data = request.get_json()
    new_post = {
        "id": len(posts_db) + 1,
        "title": data.get("title"),
        "content": data.get("content"),
        "author_id": data.get("author_id")
    }
    posts_db.append(new_post)
    return jsonify({"status": "success", "message": "Đã tạo bài viết", "data": new_post}), 201

@app.route('/api/v1/posts/', methods=['GET', 'DELETE'])
def handle_single_post(post_id):
    post = next((p for p in posts_db if p["id"] == post_id), None)
    
    if not post:
        return jsonify({"status": "error", "message": "Không tìm thấy"}), 404

    if request.method == 'GET':
        return jsonify({"status": "success", "data": post}), 200

    if request.method == 'DELETE':
        posts_db.remove(post)
        return jsonify({"status": "success", "message": "Đã xóa bài viết"}), 200

if __name__ == '__main__':
    app.run(debug=True)