from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource
from root import mongo


from root.auth.auth import getAccessTokens
from root.utilis import getUserSnippet, uniqueId

mdb = mongo.db


class ProfileSetup(Resource):
    def post(self):
        inputData = request.get_json(silent=True)

        # Check for valid input data and required keys
        if not inputData or "values" not in inputData:
            return {
                "status": 0,
                "class": "error",
                "message": "Oops! Looks like you're missing something. Double-check and let's try again with Ease Billz! 😅",
            }

        # Extracting values from the input data
        values = inputData.get("values", {})
        restaurantName = values.get("restaurantName", "")
        restaurantType = values.get("restaurantType", "")
        gstRegistered = values.get("gstRegistered", "")
        gstPercentage = values.get("gstPercentage", "")

        mobileNumber = inputData.get("mobileNumber")

        if not mobileNumber:
            return {
                "status": 0,
                "class": "error",
                "message": "We need your number to proceed with Ease Billz! Drop your digits and let's continue! 📱",
            }
        uid = uniqueId(digit=5, isNum=True, prefix=f"U")
        userInfo = {
            "_id": uid,
            "restaurantName": restaurantName,
            "restaurantType": restaurantType,
            "gstRegistered": gstRegistered,
            "mobile": mobileNumber,
        }

        if gstRegistered == "Yes":
            userInfo["gstPercentage"] = gstPercentage

        token = getAccessTokens(userInfo)
        insertResult = mdb["users"].insert_one({**userInfo, **token})

        if insertResult.inserted_id:
            return {
                "status": 1,
                "class": "success",
                "message": "Welcome to Ease Billz! You're all set to simplify your restaurant billing! 🌟",
                "payload": {"userInfo": userInfo, **token},
            }
        else:
            return {
                "status": 0,
                "class": "error",
                "message": "Yikes! Something went wrong on our end 😬. Please hold tight while we sort it out with Ease Billz!",
            }



