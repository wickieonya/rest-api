from flask import Blueprint, request, make_response, jsonify

from app.models import User, BlacklistToken

users = Blueprint("users", __name__)


@users.route("/users/register", methods=["POST"])
def new_user():
    """User registeration resource."""

    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if username is None or password is None:
        return make_response(
            jsonify(
                {"status": "fail", "message": "missing argument username/password"}
            ),
            400,
        )

    if User.query.filter_by(username=username).first() is not None:
        return make_response(
            jsonify(
                {
                    "status": "fail",
                    "message": "Username already registered. Please log in.",
                }
            ),
            202,
        )

    if User.query.filter_by(email=email).first() is not None:
        return make_response(
            jsonify(
                {
                    "status": "fail",
                    "message": "Email already registered. Please log in.",
                }
            ),
            202,
        )

    user = User(username=username, email=email, password=password)
    user.save()

    auth_token = user.encode_auth_token(user.id)

    response = {
        "status": "success",
        "message": "Successfully registered.",
        "auth_token": auth_token.decode(),
    }
    return make_response(jsonify(response), 401)


@users.route("/users/login", methods=["POST"])
def user_login():
    data = request.get_json()
    try:
        # fetch user
        user = User.query.filter_by(email=data.get("email")).first()
        auth_token = user.encode_auth_token(user.id)

        if auth_token:
            response = {
                "status": "success",
                "message": "Successfully logged in.",
                "auth_token": auth_token.decode(),
            }
            return make_response(jsonify(response), 200)

        else:
            response = {
                "status": "fail",
                "message": "User with those details does not exist.",
            }
            return make_response(jsonify(response), 404)

    except Exception as e:
        print(e)
        response = {"status": "fail", "message": "Try again."}
        return make_response(jsonify(response), 500)


@users.route("/users/status")
def user_status():
    auth_header = request.headers.get("Authorization")
    if auth_header:
        auth_token = auth_header.split(" ")[1]
    else:
        auth_token = ""
    if auth_token:
        response = User.decode_auth_token(auth_token)

        if not isinstance(response, str):
            user = User.query.filter_by(id=response).first()
            response = {
                "status": "success",
                "data": {
                    "user_id": user.id,
                    "email": user.email,
                    "admin": user.admin,
                    "registered_on": user.registered_on,
                },
            }

            return make_response(jsonify(response), 200)

        response = {"status": "fail", "message": response}

        return make_response(jsonify(response), 401)

    else:
        response = {"status": "fail", "message": "Provide a vaild auth token."}
        return make_response(jsonify(response), 401)


@users.route("/users/logout", methods=["POST"])
def user_logout():
    """Logout resource."""
    auth_header = request.headers.get("Authorization")
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            response = {"status": "fail", "message": "Bearer token malformed."}
            return make_response(jsonify(response), 401)

    else:
        auth_token = ""
    if auth_token:
        response = User.decode_auth_token(auth_token)
        if not isinstance(response, str):
            # mark the token as blacklisted
            blacklist_token = BlacklistToken(token=auth_token)
            try:
                # insert the token
                blacklist_token.save()
                response = {"status": "success", "message": "Successfully logged out."}
                return make_response(jsonify(response), 200)
            except Exception as e:
                response = {"status": "fail", "message": e}
                return make_response(jsonify(response), 200)
        else:
            response = {"status": "fail", "message": response}
            return make_response(jsonify(response), 401)

    else:
        response = {"status": "fail", "message": "Provide a valid auth token."}
        return make_response(jsonify(response), 403)
