# app.py - Bài 1: Hello API
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    # This return statement must be indented
    return {"message": "Hello, API!"}

if __name__ == "__main__":
    # This run command must also be indented
    app.run(host="127.0.0.1", port=5000, debug=True)