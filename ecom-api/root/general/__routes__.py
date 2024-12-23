from root.general.currentUser import CurrentUser
from root.storage.models import FileUpload
from . import general_api

general_api.add_resource(CurrentUser, "/currentUser", endpoint="CurrentUser")
general_api.add_resource(FileUpload, "/file/upload", endpoint="FileUpload")
