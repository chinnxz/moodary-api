from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)
from src.database import User, UserSchema, Palette, Color
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from flasgger import swag_from
import uuid

auth = Blueprint("auth", __name__, url_prefix="/api/auth")

# Register
@auth.route("/", methods=["POST"])
@swag_from("./docs/auth/register.yaml")
def register():
    username = request.json["username"]
    password = request.json["password"]
    email = request.json["email"]
    name = request.json["name"]
    surname = request.json["surname"]
    phone_number = request.json["phone_number"]

    if len(username) < 6:
        return jsonify({"error": "Username is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({"error": "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if len(password) < 6:
        return jsonify({"error": "Password is too short"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({"error": "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "Username is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)
    new_user_id = uuid.uuid4().hex
    user = User(
        id=new_user_id,
        username=username,
        password=pwd_hash,
        email=email,
        name=name,
        surname=surname,
        phone_number=phone_number,
    )
    user.save()

    new_palette_id = uuid.uuid4().hex
    new_palette = Palette(id=new_palette_id, user_id=new_user_id)
    new_palette.save()

    init_colors = [
        {"mood": 1, "code": "83C3FF"},
        {"mood": 2, "code": "FF7373"},
        {"mood": 3, "code": "B37CF9"},
        {"mood": 4, "code": "97E435"},
        {"mood": 5, "code": "FFAD62"},
    ]

    for color in init_colors:
        new_color = Color(id=uuid.uuid4().hex, palette_id=new_palette_id, color=color["code"], mood=color["mood"])
        new_color.save()

    return jsonify({"message": "User created", "user": {"username": username, "email": email}}), HTTP_201_CREATED


# Login
@auth.route("/login", methods=["POST"])
@swag_from("./docs/auth/login.yaml")
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return (
                jsonify(
                    {"user": {"refresh": refresh, "access": access, "username": user.username, "email": user.email}}
                ),
                HTTP_200_OK,
            )

    return jsonify({"error": "Wrong credentials"}), HTTP_401_UNAUTHORIZED

@auth.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({"access": access}), HTTP_200_OK
