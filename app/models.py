from app import db, bcrypt
import datetime
import os
import jwt


class User(db.Model):
    """ User model for storing user related details."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, index=True)
    password = db.Column(db.String)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, username, email, password, admin=False):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, os.environ.get("BCRYPT_LOG_ROUNDS")
        )
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def verify_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """

        try:
            payload = {
                "exp": datetime.datetime.utcnow()
                + datetime.timedelta(days=0, seconds=5),
                "iat": datetime.datetime.utcnow(),
                "sub": user_id,
            }
            return jwt.encode(payload, os.environ.get("SECRET_KEY"), algorithm="HS256")
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, os.environ.get("SECRET_KEY"))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return {
                    "status": "fail",
                    "message": "Token blacklisted. Please log in again.",
                }
            else:
                return payload["sub"]

        except jwt.ExpiredSignatureError:
            return {
                "status": "fail",
                "message": "Signature expired. Please log in again.",
            }

        except jwt.InvalidTokenError:
            return {"status": "fail", "message": "Invalid token. Please log in again."}


class BlacklistToken(db.Model):
    """
    Token model for storing JWT tokens.
    """

    __tablename__ = "blacklist_tokens"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String, unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return f"<id: token: {self.token}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        response = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if response:
            return True
        else:
            return False


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    academic_level = db.Column(db.String(128))
    type_of_paper = db.Column(db.String(120))
    discipline = db.Column(db.String(120))
    topic = db.Column(db.String(120))
    paper_instructions = db.Column(db.Text)
    additional_materials = db.Column(db.String(2048))
    paper_format = db.Column(db.String(30))
    deadline = db.Column(db.DateTime)
    pages = db.Column(db.Integer)
    spacing = db.Column(db.String(20))
    sources = db.Column(db.Integer)
    charts = db.Column(db.Integer)
    powerpoint_slides = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    messages = db.relationship("Message", backref="order", lazy="dynamic")

    status = db.Column(db.String(128), default="Pending payment")
    progress = db.Column(db.Integer, default=0)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    modified_on = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
    paid = db.Column(db.Boolean, default=False)
    files = db.relationship("File", backref="order")

    def get_status(self):
        status_list = [
            "Finished",
            "Revision",
            "Done",
            "Writer Assigned",
            "Approved",
            "Canceled",
            "Dispute",
            "Pending payment",
            "Processing",
        ]
        if self.status not in status_list:
            self.status = "Processing"

    def save(self):
        db.session.add(self)
        db.session.commit()


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    subject = db.Column(db.String, default="New Message")
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))

    @staticmethod
    def get_all():
        return Message.query.all()

    def __repr__(self):
        return f"<Message id: {self.id}>"


class File(db.Model):
    __tablename__ = "files"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    uploaded_on = db.Column(db.DateTime)
    description = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"))


class Payment(db.Model):
    """A class to represent our payments"""

    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
