import calendar
import datetime
from flask import request
from root.ipInfo import IPInfo


def getHostNameAndIp():
    data = {
        "ip": None,
        "ipv": "1",
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

        """
        Check if user ip in allowed subnet.
        Return 403 denied otherwise.
        """

    return data


def getSisHeaders():
    headers = request.headers

    return {
        "appSecureScreen": headers.get("Upappsecurescreen", False),
        "appPlatformCode": headers.get("Upappplatformcode"),
        "appVersionCode": headers.get("Upappversioncode"),
        "appVersionName": headers.get("Upappversionname"),
        "appVersionNumber": headers.get("Upappversionnumber"),
    }

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

    data = {
        **data,
        **getSisHeaders(),
    }
    # al = request.accept_languages
    # data['ral'] = al

    return data

def timestamp():
    # Timestamp
    d = datetime.utcnow()
    return calendar.timegm(d.utctimetuple())

def getUserSnippet(uid, isNew=False, tokenInfo=None, includeIp=True, time=None):
    sessionInfo = uid

    ip = getHostNameAndIp()
    ua = getUserAgents()

    time = time if time else timestamp()

    meta = (
        {"createdAtUnix": time, "createdBy": sessionInfo}
        if isNew
        else {"updatedAtUnix": time, "updatedBy": sessionInfo}
    )

    if includeIp:
        return {**meta, "ip": ip, "ua": ua}

    return meta