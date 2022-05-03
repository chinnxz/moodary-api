from datetime import date, datetime
from flask import Blueprint, jsonify, request
from src.constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from src.database import (
    User,
    db,
    Diary,
    DiarySchema,
    Hashtag,
    HashtagSchema,
    DiaryHashtagSchema,
    DiaryMonthlyMoodSchema,
)
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from
from sqlalchemy import func
from src.tag_model import tag_model
from src.functions import create_date_string, convert_mood, convert_level

import uuid
import pandas as pd
import random

diary = Blueprint("diary", __name__, url_prefix="/api/diary")


# use to add a new diary and edit selected day diary
@diary.route("/", methods=["POST"])
@jwt_required()
@swag_from("./docs/diary/post_diary.yaml")
def post_diary():
    current_user = get_jwt_identity()
    data = request.get_json()

    diary_date = data.get("date")
    date_obj = datetime.strptime(diary_date, "%d-%m-%Y")

    check_diary = Diary.get_diary(current_user, date_obj)

    mood = data.get("mood")
    c_mood = convert_mood(mood)

    # check diary on that day and delete
    if check_diary:
        prv_diary = Diary.get_diary(current_user, date_obj)
        prv_diary.delete()

    new_diary_id = uuid.uuid4().hex
    new_diary = Diary(
        id=new_diary_id,
        user_id=current_user,
        date=date_obj,
        mood=data.get("mood"),
        level=data.get("level"),
        note=data.get("note"),
    )
    new_diary.save()

    hashtags = data.get("hashtags")
    for tag in hashtags:
        new_hashtag_id = uuid.uuid4().hex
        hashtag = Hashtag(
            id=new_hashtag_id, tag=tag, diary_id=new_diary_id, mood=c_mood, level=convert_level(data.get("level"))
        )
        hashtag.save()

    serializer = DiarySchema()
    data = serializer.dump(new_diary)

    return jsonify({"message": "Diary created"}), HTTP_201_CREATED


# use to get diary by date and user_id
@diary.route("/get-diary", methods=["GET"])
@jwt_required()
@swag_from("./docs/diary/get_diary.yaml")
def get_diary_by_date():
    current_user = get_jwt_identity()
    date = request.args.get("date")
    print(date)
    date_obj = datetime.strptime(date, "%d-%m-%Y")
    print("the date is: ", date_obj)
    diary = Diary.get_diary(current_user, date_obj)

    serializer = DiarySchema()

    data = serializer.dump(diary)

    return jsonify(data), HTTP_200_OK


# use to get monthly mood to show in the calendar
@diary.route("get-monthly-mood", methods=["GET"])
@jwt_required()
@swag_from("./docs/diary/get_monthly_mood.yaml")
def get_monthly_mood():
    current_user = get_jwt_identity()
    req = request.get_json()
    month = req.get("month")
    year = req.get("year")
    date_string = create_date_string(month, year)

    q = (
        db.session.query(Diary.date, Diary.mood)
        .filter(Diary.user_id == current_user)
        .filter(Diary.date >= date_string.start_date)
        .filter(Diary.date <= date_string.end_date)
    )

    serializer = DiaryMonthlyMoodSchema(many=True)
    data = serializer.dump(q)

    return jsonify({"data": data, "message": "ok"}), HTTP_200_OK


# api for tag suggestion model and get user suggested tags
@diary.route("user-hashtag", methods=["GET"])
@jwt_required()
@swag_from("./docs/diary/hashtag_suggestion.yaml")
def hashtag_suggestion():
    current_user = get_jwt_identity()
    req = request.get_json()
    mood = req.get("mood")
    level = req.get("level")

    h_mood = convert_mood(mood)
    h_level = convert_level(level)
    q = (
        db.session.query(
            Diary.user_id, Hashtag.tag, Hashtag.mood, Hashtag.level, func.count(Hashtag.tag).label("count")
        )
        .join(Hashtag, Hashtag.diary_id == Diary.id)
        .filter(Diary.user_id == current_user, Hashtag.mood == h_mood, Hashtag.level == h_level)
        .group_by(Diary.user_id, Hashtag.tag, Hashtag.mood, Hashtag.level)
        .order_by(func.count(Hashtag.tag).desc().label("count"))
        .limit(6)
        .all()
    )

    serializer = DiaryHashtagSchema(many=True)

    if len(q) != 6:
        if len(q) > 0 and len(q) < 6:
            df = pd.DataFrame(q, columns=["id", "tag", "mood", "level", "count"])
            q_df = df.iloc[:, [1]]
            q_tag_list = q_df["tag"].to_list()
            tag_s_list = tag_model(q[0]["tag"], mood)
            check_tag_count = 0
            for tag_s in tag_s_list:
                for q_tag in q_tag_list:
                    if q_tag == tag_s:
                        break
                    else:
                        check_tag_count = check_tag_count + 1
                if check_tag_count == len(q_tag_list):
                    q_tag_list.append(tag_s)
                    if len(q_tag_list) == 6:
                        break

            mood_val = [mood] * 6
            result_df = pd.DataFrame(list(zip(q_tag_list, mood_val)), columns=["tag", "mood"])
            result_tuples = result_df.to_records(index=False)
            result = list(result_tuples)
            hashtag_data = serializer.dump(result)
            return jsonify({"data": hashtag_data, "message": "ok"}), HTTP_200_OK

        if len(q) == 0:
            hashtags = Hashtag.get_by_mood_and_level(Hashtag, h_mood)
            rand_hashtags_list = random.choices(hashtags, k=6)
            print(rand_hashtags_list)
            mood_val = [mood] * 6
            result_df = pd.DataFrame(list(zip(rand_hashtags_list, mood_val)), columns=["tag", "mood"])
            result_tuples = result_df.to_records(index=False)
            result = list(result_tuples)
            hashtag_data = serializer.dump(result)
            return jsonify({"data": hashtag_data, "message": "ok"}), HTTP_200_OK

    hashtag_data = serializer.dump(q)
    return jsonify({"data": hashtag_data, "message": "ok"}), HTTP_200_OK


@diary.errorhandler(404)
def not_found(error):
    return jsonify({"message": "404 Not Found"}), HTTP_404_NOT_FOUND


@diary.errorhandler(500)
def internal_server(error):
    return jsonify({"message": "There is a problem"}), HTTP_500_INTERNAL_SERVER_ERROR
