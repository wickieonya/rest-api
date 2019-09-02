import unittest

from flask import current_app
from flask_testing import TestCase

from app import create_app

import os


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        config_name = os.environ.get("APP_SETTINGS")
        app = create_app(config_name)

        return app

    def test_app_is_in_development(self):
        self.assertTrue(current_app.config["DEBUG"] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            current_app.config["SQLALCHEMY_DATABASE_URI"] == "postgresql://rest_api_dev"
        )


class TestTestingConfig(TestCase):
    def create_app(self):
        config_name = os.environ.get("APP_SETTINGS")
        app = create_app(config_name)

        return app

    def test_app_is_in_testing(self):
        self.assertTrue(current_app.config["DEBUG"])
        self.assertTrue(
            current_app.config["SQLALCHEMY_DATABASE_URI"]
            == "postgresql://rest_api_test"
        )
