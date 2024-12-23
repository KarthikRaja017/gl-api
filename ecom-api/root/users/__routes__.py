from root.users.otp import GenerateOtp, OtpVerification
from root.users.profile import ProfileSetup
from . import users_api


users_api.add_resource(GenerateOtp, "/request/otp")
users_api.add_resource(OtpVerification, "/verification/otp")
users_api.add_resource(ProfileSetup, "/profile/setup")
