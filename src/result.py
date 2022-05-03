from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from flask import Blueprint, jsonify, request
from src.database import Result, ResultSchema
from flask_jwt_extended import get_jwt_identity, jwt_required
from src.functions import create_date_string, query_mood_and_tag, MoodSummary
from datetime import datetime
from flasgger import swag_from
import uuid

result = Blueprint("result", __name__, url_prefix="/api/result")


class MoodResult:
    def __init__(self, total, summary):
        self.mood_total = total
        self.mood_summary = summary


@result.route("/get-result", methods=["GET"])
@jwt_required()
@swag_from("./docs/result/get_monthly_result.yaml")
def get_monthly_result():
    req = request.get_json()
    current_user = get_jwt_identity()
    month = req.get("month")
    year = req.get("year")
    date_string = create_date_string(month, year)
    total_mood = []
    mood_summary = []

    for i in range(1, 6):
        summary = query_mood_and_tag(current_user, i, date_string)
        total_mood.append(summary.mood)
        mood_summary.append(MoodSummary(i, summary.percent, summary.hashtag))

    result_mood = MoodResult(total_mood, mood_summary)

    new_result_id = uuid.uuid4().hex
    new_result = Result(
        id=new_result_id,
        user_id=current_user,
        result_mood=result_mood,
        start_date=datetime.strptime(date_string.start_date, "%d-%m-%Y"),
        end_date=datetime.strptime(date_string.end_date, "%d-%m-%Y"),
    )

    serializer = ResultSchema()
    data = serializer.dump(new_result)

    return jsonify({"data": data}), HTTP_200_OK
