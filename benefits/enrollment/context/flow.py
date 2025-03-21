from dataclasses import dataclass


@dataclass
class EnrollmentSuccess:
    success_message: str
    thank_you_message: str
