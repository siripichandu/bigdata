from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

# Sample data
items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]

# Dummy user data for authentication (you should use a proper database)
users = {"gc1": "pass1", "gc2": "pass2"}


@app.route("/", methods=["GET"])
def home_page():
    return jsonify("Welcome to land of free access")


@app.route("/help", methods=["GET"])
def help():
    return jsonify('curl -u "username:pwd" http://127.0.0.1/items')


@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username


## Enable this after testing for wrong password

# @auth.error_handler
# def unauthorized():
#     return jsonify({"message": "Sorry the password you entered is not right"}), 401


@app.route("/items", methods=["GET"])
@auth.login_required
def get_items():
    return jsonify(items)
    # return jsonify("logged in user : ", auth.username(), "items requested : ", items)


if __name__ == "__main__":
    app.run(port=5003)