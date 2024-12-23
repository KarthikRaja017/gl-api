from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    verify_jwt_in_request,
)
from functools import wraps
from root import mongo
from root.config import G_ACCESS_EXPIRES

mdb = mongo.db


def auth_required(**kwargs):
    amac = kwargs.get("amac")
    isOptional = kwargs.get("isOptional", False)

    def _decorator(fn):
        @jwt_required(optional=isOptional)
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request(optional=isOptional)

            uid = get_jwt_identity()

            if isOptional and not uid:
                return fn(*args, **kwargs, uid=None, user=None)

            user = getAuthUser(uid['uid'])

            # status = user.get("status", "")
            # if status in ["deleted", "removed", "suspended"]:
            #     return {
            #         "status": 0,
            #         "message": "Invalid Access. Please login again",
            #         "payload": {
            #             "redirectUrl": "/user/login",
            #             "logout": True
            #         }
            #     }, 401

            # if not (user and "_id" in user):
            #     return {
            #         "status": 0,
            #         "message": "Invalid Access. Please login again",
            #         "payload": {"redirectUrl": "/user/login", "logout": True},
            #     }, 403

            # if amac and not validateAccess(uid, user, amac):
            #     return {
            #         "status": 0,
            #         "message": "Unauthorized Access",
            #         "payload": {"redirectUrl": "/"},
            #     }, 401

            return fn(*args, **kwargs, uid=uid["uid"], user=user)

        return wrapper

    return _decorator


def validateAccess(uid, user, amac):
    if not user or not (user and "_id" in user and "ut" in user):
        return False

    if user["ut"] == "sa":
        return True

    if (
        user.get("amac", None)
        and user["ut"] in ["aa", "a"]
        and (amac not in user["amac"])
    ):
        return False

    # if not isCouncilUserType(user["ut"]):
    #     return False

    return True


def getAuthUser(uid, fields=None):
    projection = {
        "_id": 1,
    }

    if fields and "retriveAll" in fields:
        projection = {"password": 0}
    elif fields:
        projection = fields

    user = mdb.users.find_one({"_id": uid}, projection)

    return user


def getAccessTokens(data):
    print(f"data: {data}")
    uid = data["_id"] if "_id" in data else ""
    username = data["username"] if "username" in data else ""
    id = data["_id"] if "_id" in data else ""

    user = UserObject(
        id=id,
        uid=uid,
        username=username,
    )

    # Convert UserObject to a dictionary before passing it
    accessToken = create_access_token(identity=user.to_dict(), expires_delta=G_ACCESS_EXPIRES)
    refreshToken = create_refresh_token(identity=user.to_dict(), expires_delta=G_ACCESS_EXPIRES)

    return {
        "accessToken": accessToken,
        "refreshToken": refreshToken,
    }


class UserObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def to_dict(self):
        return self.__dict__