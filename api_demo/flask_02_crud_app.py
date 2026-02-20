from flask import Flask, jsonify, request

app = Flask(__name__)

# Sample data
items = [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]


# Show Home page
@app.route("/", methods=["GET"])
def home_page():
    return jsonify("Hello World")


# Get All Items


@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)


# Get Specific Item
@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    # Using Python Generator and Iterator (next)
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return jsonify(item)
    return jsonify({"message": "Item not found"}), 404


# Create a new Item
@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    new_item = {"id": len(items) + 1, "name": data["name"]}
    items.append(new_item)
    return jsonify(new_item), 201


# Update existing Item
@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    data = request.get_json()
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        item["name"] = data["name"]
        return jsonify(item)
    return jsonify({"message": "Item not found"}), 404


# Delete Existing Item
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global items
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        items = [i for i in items if i["id"] != item_id]
        return jsonify({"message": "Item deleted"})
    return jsonify({"message": "Item not found"}), 404


if __name__ == "__main__":
    app.run(port=5002)