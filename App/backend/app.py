from apiflask import APIFlask
from flask import Flask, jsonify

app = APIFlask(__name__)

# Home route
@app.route("/")
def home():
    return "Welcome to my Flask application!"

# Hello route
@app.route("/api/hello")
def hello():
    return jsonify({
        "message": "Hello from Flask!"
    })

# Users route
@app.route("/api/users")
def get_users():
    users = [
        {"id": 1, "name": "Ahmed"},
        {"id": 2, "name": "Skandar"},
        {"id": 3, "name": "Ali"}
    ]

    return jsonify(users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)