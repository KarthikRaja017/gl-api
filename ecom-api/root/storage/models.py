from flask import request
from flask_restful import Resource
from PIL import Image
from werkzeug.utils import secure_filename
import os
from firebase_admin import storage, credentials
from root import mongo
from root.auth.auth import auth_required
from root.config import G_TEMP_PATH


mdb = mongo.db

bucket = storage.bucket()

class FileUpload(Resource):
    @auth_required(isOptional=True)
    def post(self, uid, user):
        # Parse request args and files
        form = request.form
        files = request.files

        # Collect form data
        fc = form.get("fc")
        vid = form.get("vid")
        testId = form.get("testId")
        inputFile = files.get("file")
        if "file" not in files:
            return {"status": 0, "msg": "No file provided"}, 400

        file = files["file"]
        fext = file.filename.split(".")[-1].lower()
        if fext == "xlsx":
            temp_path = os.path.join(G_TEMP_PATH, file.filename)
            file.save(temp_path)

            try:
                response = ExtractProgramsFromExcel(vid, uid, user, path=temp_path)
            finally:
                os.unlink(temp_path)

        else:
            response = fileUploadHandler(
                uid=uid, ruid=uid, fc=fc, inputFile=inputFile, testId=testId, vid=vid
            )

        return response


def fileUploadHandler(
    uid, ruid, fc, inputFile, testId=None, fileMeta=None, isWrite=False, vid=None
):
    dbFiles = mdb["files"]

    if not fc:
        return {"status": 0, "cls": "danger", "msg": "File category not found"}

    filename = secure_filename(inputFile.filename)
    file_extension = os.path.splitext(filename)[1]
    file_type = inputFile.content_type

    bucket = storage.bucket()
    blob = bucket.blob(f"{uid}/{filename}")
    blob.upload_from_file(inputFile, content_type=file_type)
    blob.make_public()
    publicUrl = blob.public_url

    fileInfo = {
        "fid": filename,
        "fext": file_extension,
        "fc": fc,
        "userName": uid,
        "name": filename,
        "url": filename,
        "publicUrl": publicUrl,
        "pa": 1,
        "ruid": ruid,
        "status": 1,
    }

    if fc in ["profileImage"] and file_type.startswith("image"):
        im = Image.open(inputFile)
        fileInfo["width"], fileInfo["height"] = im.size

    if fileMeta:
        fileInfo.update(fileMeta)

    # if fc == "questionAttachment":
    #     dbFiles.update_one(
    #         {"_id": filename, "testId": testId, "attachmentNo": filename},
    #         {"$set": fileInfo},
    #         upsert=True,
    #     )
    # else:
    dbFiles.update_one({"_id": uid + "-" + filename}, {"$set": fileInfo}, upsert=True)

    return fileInfo
