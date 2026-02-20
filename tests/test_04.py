import unittest
import json
from flask import Flask
from api_demo.flask_04_jwt_auth_app import (
    app,
    jwt,
)  # Make sure to import your actual app


class JWTTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_hello_world(self):
        # Test the unprotected route
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode(), "Hello, World!")

    def test_login_valid_user(self):
        # Test login with valid credentials
        login_data = json.dumps({"username": "user1", "password": "password1"})
        response = self.app.post(
            "/login", headers={"Content-Type": "application/json"}, data=login_data
        )
        self.assertEqual(response.status_code, 200)
        access_token = json.loads(response.data.decode())["access_token"]
        self.assertTrue(access_token)

    def test_login_invalid_user(self):
        # Test login with invalid credentials
        login_data = json.dumps({"username": "user1", "password": "wrongpassword"})
        response = self.app.post(
            "/login", headers={"Content-Type": "application/json"}, data=login_data
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("Bad username or password", response.data.decode())

    def test_access_protected_route(self):
        # First, login to get the access token
        login_data = json.dumps({"username": "user1", "password": "password1"})
        response = self.app.post(
            "/login", headers={"Content-Type": "application/json"}, data=login_data
        )
        access_token = json.loads(response.data.decode())["access_token"]

        # Access protected route with the token
        response = self.app.get(
            "/items", headers={"Authorization": f"Bearer {access_token}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue("Item 1" in response.data.decode())

    def test_access_protected_route_without_token(self):
        # Access protected route without the token
        response = self.app.get("/items")
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()