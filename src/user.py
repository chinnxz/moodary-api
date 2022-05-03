from flask import Blueprint, jsonify, request
from src.database import db, User, UserSchema
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
import validators

user = Blueprint("user", __name__, url_prefix="/api/user")

# GET User Data
@user.route("/", methods=["GET"])
@jwt_required()
@swag_from("./docs/user/get_user_data.yaml")
def get_user_data():
    user_id = get_jwt_identity()
    user = User.get_by_id(user_id)
    serializer = UserSchema()

    data = serializer.dump(user)

    return jsonify(data), HTTP_200_OK


# EDIT User Data
@user.route("/", methods=["PUT"])
@jwt_required()
@swag_from("./docs/user/edit_user_data.yaml")
def edit_user_data():
    user_id = get_jwt_identity()
    user_to_edit = User.get_by_id(user_id)
    req = request.get_json()
    edit_username = req.get("username")
    edit_name = req.get("name")
    edit_surname = req.get("surname")
    edit_phone_number = req.get("phone_number")
    edit_email = req.get("email")
    edit_password = req.get("password")

    if len(edit_username) >= 6 and edit_username != user_to_edit.username:
        user_to_edit.username = edit_username
    elif len(edit_username) >= 6 and edit_username == user_to_edit.username:
        user_to_edit.username = user_to_edit.username
    else:
        return jsonify({"error": "Username is too short"}), HTTP_400_BAD_REQUEST

    if not edit_username.isalnum() or " " in edit_username:
        return jsonify({"error": "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if len(edit_password) >= 6 and check_password_hash(user_to_edit.password, edit_password) == False:
        user_to_edit.password = generate_password_hash(edit_password)
    elif len(edit_password) >= 6 and check_password_hash(user.password, edit_password) == True:
        user_to_edit.password = user_to_edit.password
    else:
        return jsonify({"error": "Password is too short"}), HTTP_400_BAD_REQUEST

    if validators.email(edit_email) and edit_email != user.email:
        user_to_edit.email = edit_email
    elif validators.email(edit_email) and edit_email == user.email:
        user_to_edit.email = user_to_edit.email
    else:
        return jsonify({"error": "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=edit_email).first() is not None:
        return jsonify({"error": "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=edit_username).first() is not None:
        return jsonify({"error": "Username is taken"}), HTTP_409_CONFLICT

    if user_to_edit.name != edit_name:
        user_to_edit.name = edit_name
    if user_to_edit.surname != edit_surname:
        user_to_edit.surname = edit_surname
    if user_to_edit.phone_number != edit_phone_number:
        user_to_edit.phone_number = edit_phone_number

    db.session.commit()

    return jsonify({"message": "User data is successfully edited"}), HTTP_200_OK
