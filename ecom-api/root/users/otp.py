import datetime
import re
import time
from flask import request
from flask_restful import Resource
# from twilio.rest import Client
import random
from root import mongo
from dateutil import parser 


from root.utilis import getUtcCurrentTime, uniqueId


mdb = mongo.db


def validate_phone_number(phone_number):
    pattern = r"^\+?[1-9]\d{1,14}$"
    return re.match(pattern, phone_number)




def generate_otp():
    return random.randint(100000, 999999)


def maskMobile(value, ifEmpty=False):
    pattern = (
        "\s*(?:\+?(\d{1,3}))?[-. (]*(\d{2})[-. )]*(\d{5})[-. ]*(\d{3})(?: *x(\d+))?\s*"
    )
    result = re.findall(pattern, value)

    if len(result) > 0:
        result = result[0]

    if not (len(result) > 3):
        return ifEmpty

    return f"{result[1]}*****{result[3]}"


def is_otp_valid(otpData, verificationCode, mobileNumber):

    if otpData["otp"] != int(verificationCode):
        return {
            "status": 0,
            "class": "error",
            "message": "Oops! That OTP doesn't match. Double-check and try again! 🔍",
            "payload": {},
        }

    # Check if OTP has expired
    current_time = getUtcCurrentTime()
    otpCreatedAt = parser.isoparse(otpData["currentTime"])
    
    

    # Check if OTP is tied to the correct phone number
    if otpData["mobileNumber"] != mobileNumber:
        return {
            "status": 0,
            "class": "error",
            "message": "Hmm... that phone number doesn't match the OTP. Check again! 📞",
            "payload": {},
        }

   

    return {
        "status": 1,
        "class": "success",
        "message": "OTP verified! You're all set to vibe! 🎉",
        "payload": {},
    }


class GenerateOtp(Resource):
    def post(self):
        inputData = request.get_json(silent=True)
        if not inputData or "mobileNumber" not in inputData:
            return {
                "status": 0,
                "class": "error",
                "message": "Oops! We need your mobile number to serve up your verification code. 📱",
                "payload": {},
            }

        mobileNumber = inputData["mobileNumber"]

        if not validate_phone_number(mobileNumber):
            return {
                "status": 0,
                "class": "error",
                "message": f"Uh-oh! {mobileNumber} doesn’t seem right. Please double-check the number and try again! 📲",
                "payload": {},
            }

        # Generate OTP
        otp = generate_otp()
        currentTime = getUtcCurrentTime()

        otpRequest = {
            "_id": uniqueId(digit=5, isNum=False, prefix=f"M"),
            "mobileNumber": mobileNumber,
            "otp": otp,
            "currentTime": currentTime.isoformat(),
            "attempts": 0,
        }
        insertResult = mdb["otpList"].insert_one(otpRequest)

        if not insertResult.acknowledged:
            return {
                "status": 0,
                "class": "error",
                "message": "Sorry! We couldn't save your OTP right now. Please try again shortly! 😬",
                "payload": {},
            }

        # messageSid = send_sms(mobileNumber, otp)
        maskMobileNumber = maskMobile(mobileNumber)
        # if messageSid is None:
        #     return {
        #         "status": 0,
        #         "class": "error",
        #         "message": f"Failed to send OTP to {maskMobileNumber}. Please check your number and try again. 🚫",
        #         "payload": {},
        #     }

        return {
            "status": 1,
            "class": "success",
            "message": f"Success! Your verification code has been sent to {maskMobileNumber}. 📩",
            "payload": otpRequest,
        }



class OtpVerification(Resource):
    def post(self):
        inputData = request.get_json(silent=True)
        otp = inputData.get("otp")
        otpRequest = inputData.get("otpRequest")
        verificationCode = otpRequest.get("otp")
        mobileNumber = inputData.get("mobileNumber")
        
        if not otp or not verificationCode or not mobileNumber:
            return {
                "status": 0,
                "class": "error",
                "message": "Whoa! Looks like we're missing a few details. Let's double-check that OTP and try again! 🔄",
                "payload": {},
            }

        otpRequest["attempts"] = otpRequest.get("attempts", 0) + 1

        response = is_otp_valid(otpRequest, otp, mobileNumber)
        currentTime = getUtcCurrentTime()

        mdb["otpList"].update_one(
            {"_id": otpRequest.get("_id")},
            {"$set": {"verificationCode": verificationCode, "updatedAt": currentTime.isoformat()}},
        )

        return response
