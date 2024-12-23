# OTP
from datetime import datetime, timedelta
import os

import firebase_admin
from flask import json

from firebase_admin import credentials



# DB
LOCAL_MONGO_URI = "mongodb://localhost:27017"
MONGO_URI = LOCAL_MONGO_URI
LOCAL_MONGO_DATABASE = "eb"
MONGO_DATABASE = LOCAL_MONGO_DATABASE

OTP_EXPIRY_TIME = 200
MAX_ATTEMPTS = 3

G_DATE_FORMAT_READABLE = "%d %b, %Y"
G_PDF_DATE_FORMAT = "%d.%m.%Y"
G_PDF_DATETIME_FORMAT = f"{G_PDF_DATE_FORMAT} %I:%M %p"

G_JWT_ACCESS_SECRET_KEY = "brklbcAm6I4TNNMCVdKQscJaSsgBSNSISfyFeb182021"

G_ACCESS_EXPIRES = timedelta(minutes=50000000)
G_REFRESH_EXPIRES = timedelta(days=30)
FERNET_KEY = b"hjrbVGCHdDsdrNW6dgOIcl0nbwEtPd5eL_whWIG2FJ8="


FBS_BUCKET = "gs://ease-billz.appspot.com"


def initialize_firebase():
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {"storageBucket": "ease-billz.appspot.com"})


# class CustomFlaskResponseEncoder(json.JSONEncoder):
#     def default(self, obj):
#         print(f"obj: {obj}")
#         if isinstance(obj, datetime.datetime):
#             return str(obj)
#         elif isinstance(obj, datetime.date):
#             return str(obj)


#         return json.JSONEncoder.default(self, obj)
class Config:
    JWT_SECRET_KEY = G_JWT_ACCESS_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = G_ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = G_REFRESH_EXPIRES
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    PROPAGATE_EXCEPTIONS = True
    # RESTFUL_JSON = {"cls": CustomFlaskResponseEncoder}


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
G_TEMP_PATH = os.path.abspath(os.path.join(ROOT_DIR, "..", "temp"))
