from flask import Blueprint
from flask_restful import Api

from root.config import initialize_firebase

general_bp = Blueprint('general', __name__, url_prefix='/server/api')
general_api = Api(general_bp)
initialize_firebase()
from . import __routes__
