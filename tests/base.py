from flask_testing import TestCase
import os

from app import create_app, db


class BaseTestCase(TestCase):
    """Base Tests"""

    def create_app(self):
        config_name = os.environ.get("APP_SETTINGS")
        app = create_app(config_name)
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
