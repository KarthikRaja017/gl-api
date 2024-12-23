from flask_restful import Resource
from root import mongo
from root.auth.auth import auth_required
from root.config import FERNET_KEY
from cryptography.fernet import Fernet

mdb = mongo.db


class CurrentUser(Resource):
    @auth_required(isOptional=True)
    def get(self, uid, user):
        print(f"uid: {uid}")
        if not uid:
            return {"status": 0, "msg": "Not logged in", "payload": {}}

        userid = user.get("_id")
        projection = {"mobile": 1, "accessToken": 1, "restaurantName": 1}
        if user:
            data = mdb.users.find_one({"_id": userid}, projection)
            # encryptedToken = encrypt_access_token(data['accessToken'])
            # data['accessToken'] = encryptedToken
        return {"status": 1, "msg": "Success", "payload": data}


def encrypt_access_token(self, access_token):
        """Encrypt the access token using Fernet symmetric encryption."""
        fernet = Fernet(FERNET_KEY)

        encrypted_token = fernet.encrypt(access_token.encode())
        return encrypted_token.decode()  