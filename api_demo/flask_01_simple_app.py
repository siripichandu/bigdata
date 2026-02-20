from flask import Flask, jsonify

app = Flask(__name__)

# Sample data
items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


@app.route("/", methods=["GET"])
def home_page():
    return jsonify("Hello World")


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)


if __name__ == "__main__":
    app.run(port=5001)