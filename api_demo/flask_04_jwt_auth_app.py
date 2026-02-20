## Java Web Tokens
from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

app = Flask(__name__)

# Configure JWT
app.config["JWT_SECRET_KEY"] = "slj234jofsjfosdijufoow4rnsgi"  # Change this secret key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 120  # Set the expiration time 120 seconds

jwt = JWTManager(app)

# Dummy user database for demonstration purposes
users = {"user1": "password1", "user2": "password2"}

# Sample data
items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello, World!"


@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)

    # Validate user credentials
    if users.get(username) != password:
        return jsonify({"msg": "Bad username or password"}), 401

    # Create JWT token
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.route("/items", methods=["GET"])
@jwt_required()
def get_items():
    current_user = get_jwt_identity()
    return jsonify(current_user, items)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=True)