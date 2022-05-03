import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.database import UserPaletteSchema, db, Palette, PaletteSchema, Color, ColorSchema
import uuid
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from flasgger import swag_from

palette = Blueprint("palette", __name__, url_prefix="/api/palette")

# get all current user palattes
@palette.route("/", methods=["GET"])
@jwt_required()
@swag_from("./docs/palette/get_palette.yaml")
def get_all_palettes():
    current_user = get_jwt_identity()
    q = (
        db.session.query(Palette.id, Color.color, Color.mood)
        .join(Color, Color.palette_id == Palette.id)
        .filter(Palette.user_id == current_user)
        .order_by(Palette.id, Color.mood)
        .all()
    )

    q_count = 0
    q_colors = []
    serializer = UserPaletteSchema(many=True)
    result = []

    for query in q:
        if q_count < 5:
            q_colors.append({"color": query["color"], "mood": query["mood"]})
            q_count = q_count + 1
        if q_count == 5:
            user_palette = {"id": query["id"], "colors": q_colors}
            result.append(user_palette)
            q_count = 0
            q_colors = []

    data = serializer.dump(result)

    return jsonify({"data": data, "message": "OK"}), HTTP_200_OK


@palette.route("/", methods=["POST"])
@jwt_required()
@swag_from("./docs/palette/create_palette.yaml")
def create_palette():
    current_user = get_jwt_identity()
    data = request.get_json()
    colors = data.get("colors")

    new_palette_id = uuid.uuid4().hex
    new_palette = Palette(id=new_palette_id, user_id=current_user)
    new_palette.save()

    for color in colors:
        new_color = Color(id=uuid.uuid4().hex, palette_id=new_palette_id, color=color["code"], mood=color["mood"])
        new_color.save()

    return jsonify(data, {"message": "OK"}), HTTP_200_OK
