import unittest
import json
from api_demo.flask_02_crud_app import app

# from sys import platform


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # @unittest.skipIf(platform.startswith("win"), "Do not run on Windows")
    def test_get_items(self):
        response = self.app.get("/items")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # assuming the response is a list

    # @unittest.skip('Yet to complete the work.')
    def test_get_item(self):
        result = {"id": 1, "name": "Item 1"}
        response = self.app.get("/items/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, result)  # assuming the response is a list

    def test_create_item(self):
        # self.skipTest('skip me for now')
        # Define the payload for the POST request
        payload = json.dumps({"name": "Item 3"})

        # Make a POST request
        response = self.app.post(
            "/items", headers={"Content-Type": "application/json"}, data=payload
        )

        # Check the status code and response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["name"], "Item 3")
        self.assertEqual(response.json["id"], 3)
        self.assertTrue("id" in response.json)

    def test_update_item(self):
        raise unittest.SkipTest("raising an alert for skipping")

        # First, create an item to update
        create_response = self.app.post(
            "/items",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"name": "Temporary Item"}),
        )
        item_id = create_response.json["id"]

        # Define the payload for the PUT request
        updated_payload = json.dumps({"name": "Updated Item"})

        # Make a PUT request to update the item
        update_response = self.app.put(
            f"/items/{item_id}",
            headers={"Content-Type": "application/json"},
            data=updated_payload,
        )

        # Check the status code and response
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json["name"], "Updated Item")

    def test_delete_item(self):
        # First, create an item to delete
        create_response = self.app.post(
            "/items",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"name": "Item to Delete"}),
        )
        item_id = create_response.json["id"]

        # Make a DELETE request
        delete_response = self.app.delete(f"/items/{item_id}")

        # Check the status code and response
        self.assertEqual(delete_response.status_code, 200)

        # Optionally, verify the item was deleted by trying to fetch it
        get_response = self.app.get(f"/items/{item_id}")
        self.assertEqual(get_response.status_code, 404)


if __name__ == "__main__":
    unittest.main()