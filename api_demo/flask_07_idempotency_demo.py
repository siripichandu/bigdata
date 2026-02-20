from flask import Flask, jsonify, request

app = Flask(__name__)

items = {
    "1": {"name": "item 1", "description": "This is item 1"},
    "2": {"name": "item 2", "description": "This is item 2"},
}


@app.route("/item/<item_id>", methods=["GET", "PUT", "DELETE"])
def manage_item(item_id):
    if request.method == "GET":
        # Check if the item exists
        if item_id in items:
            return jsonify({"item": items[item_id]}), 200
        else:
            # Return 404 if the item is not found
            return jsonify({"message": "item not found."}), 404

    elif request.method == "PUT":
        # Get the JSON data from the request body
        data = request.get_json()

        # If the item exists, update it
        if item_id in items:
            items[item_id].update(data)
            return jsonify(
                {
                    "message": f"item {item_id} updated successfully.",
                    "item": items[item_id],
                }
            ), 200
        else:
            # If the item doesn't exist, create it
            items[item_id] = data
            return jsonify(
                {
                    "message": f"item {item_id} created successfully.",
                    "item": items[item_id],
                }
            ), 201

    elif request.method == "DELETE":
        # Check if the item exists
        if item_id in items:
            del items[item_id]
            return jsonify({"message": f"item {item_id} deleted successfully."}), 200
        else:
            # If item is already deleted or doesn't exist, return 204 No Content
            return jsonify({"message": "item not found or already deleted."}), 204


if __name__ == "__main__":
    app.run(debug=True)