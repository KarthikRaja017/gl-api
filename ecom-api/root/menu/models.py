from flask import json, request
from flask_restful import Resource
from root import mongo

from root.auth.auth import auth_required
from root.utilis import Status, getUserSnippet, uniqueId

mdb = mongo.db


class AddMenu(Resource):
    @auth_required(isOptional=True)
    def post(self, uid, user):
        inputData = request.get_json(silent=True)
        menus = inputData["values"]
        menuName = menus.get("name")

        existingMenu = mdb["menus"].find_one({"uid": uid, "name": menuName})

        if existingMenu:
            return {
                "status": 0,
                "message": f"Oops! A menu item named '{menuName}' already exists. Try a unique name for your new dish!",
                "payload": None,
            }
        mid = uniqueId(digit=5, isNum=True, prefix=f"M")
        menuInfo = {
            "_id": mid,
            "uid": uid,
            "status": Status.ACTIVE.value,
            **menus,
            **getUserSnippet(uid, True),
        }
        mdb["menus"].insert_one(menuInfo)
        return {
            "status": 1,
            "message": f"Success! 🎉 Your menu '{menuName}' is live and ready to be savored! "
            "Keep the creativity going — add more delicious options to your menu lineup!",
            "payload": menuInfo,
        }


class GetMenu(Resource):
    @auth_required(isOptional=True)
    def get(self, uid, user):
        menuItems = []
        menus = mdb["menus"].find(
            {"uid": uid, "status": Status.ACTIVE.value},
            {"name": 1, "price": 1, "category": 1},
        )
        for items in menus:
            menuItems.append(items)
        totalRecord = mdb["menus"].count_documents({"uid": uid})

        return {
            "status": 1,
            "message": "Success!",
            "payload": {"menuItems": menuItems, "totalRecord": totalRecord},
        }


class DeleteMenu(Resource):
    @auth_required(isOptional=True)
    def get(self, uid, user):
        args = request.args
        recordStr = args.get("record")
        record = json.loads(recordStr)
        mid = record.get("_id")
        menu = record.get("name")
        mdb["menus"].update_one(
            {"uid": uid, "_id": mid},
            {
                "$set": {
                    "status": Status.REMOVED.value,
                    **getUserSnippet(uid, False),
                }
            },
        )
        return {
            "status": 1,
            "cls": "success",
            "message": f"{menu} Menu Deleted Successfully",
        }
