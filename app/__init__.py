from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from config import app_config

db = SQLAlchemy()
bcrypt = Bcrypt()


def create_app(config_name):
    app = FlaskAPI(__name__)
    app.config.from_object(app_config[config_name])

    # init extensions
    db.init_app(app)
    bcrypt.init_app(app)

    from app.views import users

    app.register_blueprint(users)

    return app
