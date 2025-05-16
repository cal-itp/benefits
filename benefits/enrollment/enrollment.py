from enum import Enum


class Status(Enum):
    # SUCCESS means the enrollment went through successfully
    SUCCESS = 1

    # SYSTEM_ERROR means the enrollment system encountered an internal error (returned a 500 HTTP status)
    SYSTEM_ERROR = 2

    # EXCEPTION means the enrollment system is working, but something unexpected happened
    # because of a misconfiguration or invalid request from our side
    EXCEPTION = 3

    # REENROLLMENT_ERROR means that the user tried to re-enroll but is not within the reenrollment window
    REENROLLMENT_ERROR = 4
