from src.database import db, Diary, Hashtag
from sqlalchemy import func


class DurDateString:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date


class MoodSummary:
    def __init__(self, mood, percent, tag):
        self.mood = mood
        self.percent = percent
        self.hashtag = tag


def create_date_string(month, year):
    match month:
        case "01":
            start_day = "01"
            end_day = "31"
        case "02":
            start_day = "01"
            is_leap = check_leap(int(year))
            if is_leap:
                end_day = "29"
            else:
                end_day = "28"
        case "03":
            start_day = "01"
            end_day = "31"
        case "04":
            start_day = "01"
            end_day = "30"
        case "05":
            start_day = "01"
            end_day = "31"
        case "06":
            start_day = "01"
            end_day = "30"
        case "07":
            start_day = "01"
            end_day = "31"
        case "08":
            start_day = "01"
            end_day = "31"
        case "09":
            start_day = "01"
            end_day = "30"
        case "10":
            start_day = "01"
            end_day = "31"
        case "11":
            start_day = "01"
            end_day = "30"
        case "12":
            start_day = "01"
            end_day = "31"
    start_date = str(start_day + "-" + month + "-" + year)
    end_date = str(end_day + "-" + month + "-" + year)
    date_string = DurDateString(start_date, end_date)
    return date_string


def check_leap(year):
    is_leap_year = False
    if (year % 400 == 0) or (year % 100 != 0) and (year % 4 == 0):
        is_leap_year = True
    else:
        is_leap_year = False
    return is_leap_year


def convert_mood(mood):
    match mood:
        case 1:
            return "sad"
        case 2:
            return "angry"
        case 3:
            return "scary"
        case 4:
            return "normal"
        case 5:
            return "happy"


def convert_level(level):
    match level:
        case 1 | 2:
            return "low"
        case 3:
            return "medium"
        case 4 | 5:
            return "high"


def query_mood_and_tag(user_id, mood, date_string):
    tag_mood = convert_mood(mood)

    q_tag = (
        db.session.query(Diary.user_id, Hashtag.tag, func.count(Hashtag.tag).label("count"))
        .join(Hashtag, Hashtag.diary_id == Diary.id)
        .filter(Diary.user_id == user_id, Hashtag.mood == tag_mood)
        .filter(Diary.date >= date_string.start_date)
        .filter(Diary.date <= date_string.end_date)
        .group_by(Diary.user_id, Hashtag.tag, Hashtag.mood)
        .order_by(func.count(Hashtag.tag).desc().label("count"))
        .first()
    )

    q_mood = (
        db.session.query(Diary.user_id, Diary.mood, func.count(Diary.mood).label("count"))
        .filter(Diary.user_id == user_id, Diary.mood == mood)
        .filter(Diary.date >= date_string.start_date)
        .filter(Diary.date <= date_string.end_date)
        .group_by(Diary.user_id, Diary.mood)
        .first()
    )

    q_diary_count = (
        db.session.query(Diary.level)
        .filter(Diary.user_id == user_id, Diary.mood == mood)
        .filter(Diary.date >= date_string.start_date)
        .filter(Diary.date <= date_string.end_date)
        .all()
    )

    q_all_diary_count = (
        db.session.query(Diary.level)
        .filter(Diary.user_id == user_id)
        .filter(Diary.date >= date_string.start_date)
        .filter(Diary.date <= date_string.end_date)
        .all()
    )

    day_count = len(q_all_diary_count)
    level_mood_sum = 0
    level_sum = 0
    for query in q_diary_count:
        level_sum += query.level
        level_mood_sum += mood * query.level

    if level_sum != 0 and day_count >= 14:
        result = (level_sum / (5 * day_count)) * 100
        percent = str(float("{:.2f}".format(result))) + "%"
        print(percent)

    if q_mood is not None and q_tag is not None:
        summary = MoodSummary(q_mood.count, percent, q_tag.tag)
    else:
        summary = MoodSummary(0, "", "")

    return summary
