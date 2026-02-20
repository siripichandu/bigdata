import unittest
from flask import Flask, jsonify, request
from api_demo.flask_03_basic_auth_app import (
    app,
    auth,
    verify_password,
)  # Make sure to import your actual app
from base64 import b64encode


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_items_without_auth(self):
        # Attempt to access a protected route without authentication
        response = self.app.get("/items")
        # Expect a 401 Unauthorized response
        self.assertEqual(response.status_code, 401)

    def test_get_items_with_auth(self):
        # Credentials
        valid_credentials = {"gc1": "pass1", "gc2": "pass2"}
        for username, password in valid_credentials.items():
            response = self.app.get(
                "/items",
                headers={
                    "Authorization": "Basic "
                    + b64encode(f"{username}:{password}".encode("utf-8")).decode(
                        "utf-8"
                    )
                },
            )
            # Expect a 200 OK response
            self.assertEqual(response.status_code, 200)

    def test_get_items_with_invalid_auth(self):
        # Wrong credentials
        response = self.app.get(
            "/items",
            headers={
                "Authorization": "Basic " + b64encode(b"gc1:wrongpass").decode("utf-8")
            },
        )
        # Expect a 401 Unauthorized response
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()