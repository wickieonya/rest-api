import unittest

from app import db
from app.models import User
from .base import BaseTestCase

import json


class TestUserModel(BaseTestCase):
    def test_encode_auth_token(self):
        user = User(
            username="wickieonya", email="wickieonya@gmail.com", password="test"
        )
        user.save()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(User.decode_auth_token(auth_token) == user.id)

    def test_registration(self):
        """Test for user registration."""
        with self.client:
            response = self.client.post(
                "/auth/register",
                data=json.dumps(
                    dict(
                        username="wickieonya",
                        email="wickieonya@gmail.com",
                        password="123456",
                    )
                ),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Sucessfully registered.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)


if __name__ == "__main__":
    unittest.main()
