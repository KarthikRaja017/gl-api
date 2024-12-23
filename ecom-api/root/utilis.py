from enum import Enum
from random import choice
import string
from flask import request
import pytz
from datetime import datetime, timezone

from root import mongo
from root.config import G_DATE_FORMAT_READABLE, G_PDF_DATETIME_FORMAT
from root.ipInfo import IPInfo

mdb = mongo.db


def numGenerator(size=6, chars=string.digits):
    return "".join(choice(chars) for x in range(size))


def getUtcCurrentTime():
    return datetime.now(tz=pytz.UTC)


def alphaNumGenerator(size=4, chars="ABCDEFGHJKLMNPQRSTUVWYZ123456789"):
    return "".join(choice(chars) for x in range(size))


def get_local_timezone():
    # Get the local timezone based on the system settings
    return datetime.now().astimezone().tzinfo


def dateTimeToReadableDate(dateTime, format=G_DATE_FORMAT_READABLE):
    if not dateTime:
        return None

    utcDateTime = dateTime.replace(tzinfo=timezone.utc)

    localTimezone = get_local_timezone()
    localDateTime = utcDateTime.astimezone(localTimezone)

    readableDateTime = localDateTime.strftime(format)
    return readableDateTime


def uniqueId(digit=4, isNum=False, ref={}, prefix=None, suffix=None):
    _id = numGenerator(digit) if isNum else alphaNumGenerator(digit)

    if prefix is not None:
        _id = f"{prefix}X{_id}"

    if suffix is not None:
        _id = f"{_id}X{suffix}"

    mUniqueIds = mdb.uuid
    data = mUniqueIds.find_one({"_id": _id})

    if data and "_id" in data:
        return uniqueId(digit, isNum, ref, prefix, suffix)
    else:
        if ref and "_id" in ref:
            ref.pop("_id")
        mUniqueIds.insert_one({"_id": _id, **ref})
        return _id


def getHostNameAndIp():
    data = {
        "ip": None,
    }
    try:
        ipinfo = IPInfo()
        data["browser"] = ipinfo.browser
        data["os"] = ipinfo.os
        data["lang"] = ipinfo.lang
        data["ipra"] = ipinfo.ipaddress

        if request.environ.get("HTTP_X_FORWARDED_FOR"):
            data["ip"] = request.environ["HTTP_X_FORWARDED_FOR"]
        else:
            data["ip"] = request.environ.get("HTTP_X_REAL_IP", request.remote_addr)

    except Exception as e:
        pass

    return data


def getUserAgents():
    data = {}

    userAgent = request.headers.get("User-Agent")
    ua = request.user_agent
    data["ruaPlatform"] = ua.platform
    data["ruaBrowser"] = ua.browser
    data["ruaVersion"] = ua.version
    data["ruaLanguage"] = ua.language
    data["ruaString"] = ua.language
    data["rua"] = userAgent
    # al = request.accept_languages
    # data['ral'] = al

    return data


def getUserSnippet(
    uid: str,
    isNew: bool = False,
    sby: dict = {},
    extra: dict = {},
    currentTime=None,
    updatePrefix="updated",
    createPrefix="created",
    includeUpdatedAt=True,
):
    ip = getHostNameAndIp()
    ua = getUserAgents()

    # Ensure currentTime is a datetime, then format it as an ISO string
    if not currentTime:
        currentTime = getUtcCurrentTime()

    # Convert datetime to ISO format for JSON serialization
    currentTimeIso = currentTime.isoformat()
    readableDate = dateTimeToReadableDate(currentTime, format=G_PDF_DATETIME_FORMAT)

    sessionBy = {}
    # if sby:
    #     if "ut" in sby:
    #         sessionBy["sut"] = sby["ut"]
    #     if "fullName" in sby:
    #         sessionBy["sname"] = sby["fullName"]
    #     if "_id" in sby:
    #         sessionBy["suid"] = sby["_id"]

    meta = {
        **extra,
        f"{updatePrefix}At": currentTimeIso,
        f"{updatePrefix}AtRf": readableDate,
        f"{updatePrefix}Uid": uid,
        f"{updatePrefix}By": sessionBy,
        f"{updatePrefix}Ip": {**ip, **ua},
    }

    if isNew:
        createdBy = {
            **extra,
            f"{createPrefix}At": currentTimeIso,
            f"{createPrefix}AtRf": readableDate,
            f"{createPrefix}Uid": uid,
            f"{createPrefix}By": sessionBy,
            f"{createPrefix}Ip": {**ip, **ua},
        }

        if includeUpdatedAt:
            meta = {**createdBy, **meta}
        else:
            meta = createdBy

    return meta


class Status(Enum):
    REMOVED = 0
    ACTIVE = 1
