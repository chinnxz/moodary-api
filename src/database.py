from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
import datetime
import uuid

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    surname = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(255), nullable=True)
    facebook_token = db.Column(db.String(512), nullable=True)
    instagram_token = db.Column(db.String(512), nullable=True)
    twitter_token = db.Column(db.String(512), nullable=True)
    diaries = db.relationship("Diary", backref="user")
    palettes = db.relationship("Palette", backref="user")
    results = db.relationship("Result", backref="user")

    def __repr__(self):
        return self.username

    @classmethod
    def get_by_id(cls, id):  # get user by id
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()


class UserSchema(Schema):
    name = fields.String()
    surname = fields.String()
    username = fields.String()
    email = fields.String()
    phone_number = fields.String()


class Diary(db.Model):
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    mood = db.Column(db.Integer(), nullable=False)
    level = db.Column(db.Integer(), nullable=False)
    note = db.Column(db.String(255), nullable=True)
    hashtags = db.relationship("Hashtag", backref="diary")

    def __repr__(self):
        return self.id

    @classmethod
    def get_all(cls, user_id):
        return cls.query.filter(user_id == user_id).all()

    @classmethod
    def get_by_id(cls, user_id, id):
        return cls.query.filter_by(user_id=user_id, id=id).first()

    @classmethod
    def get_diary(cls, user_id, date):
        return cls.query.filter_by(user_id=user_id, date=date).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class DiarySchema(Schema):
    date = fields.DateTime()
    mood = fields.Integer()
    level = fields.Integer()
    note = fields.String()
    hashtags = fields.List(fields.String())


class DiaryHashtagSchema(Schema):
    tag = fields.String()
    mood = fields.String()


class DiaryMonthlyMoodSchema(Schema):
    date = fields.DateTime()
    mood = fields.Integer()


class Hashtag(db.Model):
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    diary_id = db.Column(db.String(32), db.ForeignKey("diary.id"))
    tag = db.Column(db.String(255), nullable=False)
    mood = db.Column(db.String(255), nullable=False)
    level = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return self.tag

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):  # get data or 404 not found
        return cls.query.get_or_404(id)

    def get_by_tag(cls, hashtag):
        return cls.query.filter_by(tag=hashtag).first()

    def get_by_mood_and_level(cls, mood):
        return cls.query.filter_by(mood=mood).distinct(cls.tag).all()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class HashtagSchema(Schema):
    id = fields.String()
    diary_id = fields.String()
    tag = fields.String()
    mood = fields.String()
    level = fields.String()


class HashtagRandomSchema(Schema):
    tag = fields.String()
    mood = fields.Integer()


class Palette(db.Model):
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    colors = db.relationship("Color", backref="palette")

    def __repr__(self):
        return self.id

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_all_palettes(cls, user_id):
        return cls.query.filter(user_id == user_id).all()

    @classmethod
    def get_by_id(cls, id):  # get data or 404 not found
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class PaletteSchema(Schema):
    id = fields.String()
    colors = fields.List(fields.String())


class Color(db.Model):
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    palette_id = db.Column(db.String(32), db.ForeignKey("palette.id"))
    color = db.Column(db.String(), nullable=False)
    mood = db.Column(db.Integer(), nullable=False)

    def __repr__(self):
        return self.id

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):  # get data or 404 not found
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_code(cls, code):  # get data or 404 not found
        return cls.query.filter_by(color=code).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class ColorSchema(Schema):
    id = fields.String()
    palette_id = fields.String()
    color = fields.String()
    mood = fields.Integer()


class UserColorSchema(Schema):
    color = fields.String()
    mood = fields.Integer()


class UserPaletteSchema(Schema):
    id = fields.String()
    colors = fields.List(fields.Nested(UserColorSchema))


class Result(db.Model):
    id = db.Column(db.String(32), default=uuid.uuid4().hex, primary_key=True)
    user_id = db.Column(db.String(32), db.ForeignKey("user.id"))
    result_mood = db.Column(db.ARRAY(db.Integer()))
    result_hashtag = db.Column(db.ARRAY(db.String()))
    result_level = db.Column(db.ARRAY(db.String()))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return self.id

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_by_id(cls, id):  # get data or 404 not found
        return cls.query.get_or_404(id)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class MoodSummarySchema(Schema):
    mood = fields.Integer()
    percent = fields.String()
    hashtag = fields.String()


class ResultMoodSchema(Schema):
    mood_total = fields.List(fields.Integer())
    mood_summary = fields.List(fields.Nested(MoodSummarySchema))


class ResultSchema(Schema):
    id = fields.String()
    user_id = fields.String()
    result_mood = fields.Nested(ResultMoodSchema)
    start_date = fields.DateTime()
    end_date = fields.DateTime()
