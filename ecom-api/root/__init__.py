import os

from flask import Flask
from flask_jwt_extended import JWTManager
from root.config import Config, initialize_firebase
from root.db import mongo
from flask_restful import Api


api = Api()
jwt = JWTManager()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    mongo.init_app(app)
    jwt.init_app(app)

    # app.register_blueprint(users)
    from root.users import users_bp
    app.register_blueprint(users_bp)
    
    from root.general import general_bp
    app.register_blueprint(general_bp)
    from root.menu import menu_bp
    app.register_blueprint(menu_bp)
    # initialize_firebase()

    return app