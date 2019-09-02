import os
from flask_migrate import Migrate


from app import create_app, db

from app.models import User, Message, Order, File

config_name = os.environ.get('APP_SETTINGS')

app = create_app(config_name)
migrate = Migrate(app, db)

@app.shell_context_processor
def ctx():
    return dict(app=app, db=db, User=User, Messages=Message, Orders=Order, File=File )

if __name__ == '__main__':
    app.run()