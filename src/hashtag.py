from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from src.database import db, Hashtag, HashtagSchema, HashtagRandomSchema
from flask_jwt_extended import get_jwt_identity, jwt_required
import uuid
import random

hashtag = Blueprint("hashtag", __name__, url_prefix="/api/hashtag")


@hashtag.route("/", methods=["GET", "POST"])
def handle_hashtags():

    if request.method == "GET":  # get hashtag
        hashtags = Hashtag.get_all()
        serializer = HashtagSchema(many=True)
        data = serializer.dump(hashtags)

        return jsonify(data)
    else:
        data = request.get_json()  # create hashtag

        new_hashtag = Hashtag(id=uuid.uuid4().hex, tag=data.get("tag"), mood=data.get("mood"), level=data.get("level"))

        new_hashtag.save()

        serializer = HashtagSchema()

        data = serializer.dump(new_hashtag)

        return jsonify(data), HTTP_201_CREATED


@hashtag.route("/<int:id>", methods=["GET"])
def get_hashtag(id):
    hashtag = Hashtag.get_by_id(id)

    serializer = HashtagSchema()

    data = serializer.dump(hashtag)

    return jsonify(data), HTTP_200_OK


@hashtag.route("/<int:id>", methods=["PUT"])
def update_hashtag(id):
    hashtag_to_update = Hashtag.get_by_id(id)

    data = request.get_json()

    hashtag_to_update.tag = data.get("tag")
    hashtag_to_update.mood = data.get("mood")
    hashtag_to_update.level = data.get("level")

    db.session.commit()

    serializer = HashtagSchema()

    hashtag_data = serializer.dump(hashtag_to_update)

    return jsonify(hashtag_data), HTTP_200_OK


@hashtag.route("/<int:id>", methods=["DELETE"])
def delete_hashtag(id):
    hashtag_to_delete = Hashtag.get_by_id(id)

    hashtag_to_delete.delete()

    return jsonify({"message": "Deleted"}), HTTP_204_NO_CONTENT


@hashtag.route("/get-mood-tag", methods=["GET"])
def get_mood_hashtags():

    req = request.get_json()

    mood = req.get("mood")
    level = req.get("level")

    match mood:
        case 1:
            c_mood = "sad"
        case 2:
            c_mood = "angry"
        case 3:
            c_mood = "scary"
        case 4:
            c_mood = "normal"
        case 5:
            c_mood = "happy"

    hashtags = Hashtag.get_by_mood_and_level(Hashtag, c_mood, level)
    rand_hashtags_list = random.choices(hashtags, k=6)

    serializer = HashtagRandomSchema(many=True)
    data = serializer.dump(hashtags)

    return jsonify({"data": data, "message": "success"}), HTTP_200_OK


@hashtag.errorhandler(404)
def not_found(error):
    return jsonify({"message": "404 Not Found"}), HTTP_404_NOT_FOUND


@hashtag.errorhandler(500)
def internal_server(error):
    return jsonify({"message": "There is a problem"}), HTTP_500_INTERNAL_SERVER_ERROR
