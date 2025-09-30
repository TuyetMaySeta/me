from enum import Enum


class VerificationTypeEnum(str, Enum):
    REGISTER = "Register"
    FORGOT_PASSWORD = "Forgot Password"
    CHANGE_EMAIL = "Change Email"
    CHANGE_PASSWORD = "Change Password"
