from flask import Blueprint
from flask_restful import Api

menu_bp = Blueprint("menu", __name__, url_prefix="/server/api")
menu_api = Api(menu_bp)
from . import routes
