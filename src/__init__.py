from flask import Flask, jsonify
import os
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.hashtag import hashtag
from src.auth import auth
from src.diaries import diary
from src.palette import palette
from src.result import result
from src.user import user
from src.database import db
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from src.config.swagger import template, swagger_config


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            SQLALCHEMY_TRACK_MODIFICATIONS=os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS"),
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            SWAGGER={"title": "Moodary API", "uiversion": 3},
        )
        print(os.environ.get("SQLALCHEMY_DATABASE_URI"))
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(hashtag)
    app.register_blueprint(auth)
    app.register_blueprint(diary)
    app.register_blueprint(palette)
    app.register_blueprint(result)
    app.register_blueprint(user)

    Swagger(app, config=swagger_config, template=template)

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def not_found(error):
        return jsonify({"message": "404 Not Found"}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server(error):
        return jsonify({"message": "There is a problem"}), HTTP_500_INTERNAL_SERVER_ERROR

    return app
