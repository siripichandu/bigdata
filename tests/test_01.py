import unittest

from api_demo.flask_01_simple_app import app


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_homepage(self):
        response = self.app.get("/")
        result = "Hello World"
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, result)  # assuming the response is a list

    def test_get_items(self):
        response = self.app.get("/items")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)  # assuming the response is a list


if __name__ == "__main__":
    unittest.main()