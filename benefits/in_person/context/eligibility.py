from dataclasses import asdict, dataclass

from benefits.core.context import SystemName


@dataclass
class EligibilityIndex:
    policy_details: str

    def dict(self):
        return asdict(self)


eligibility_index = {
    SystemName.OLDER_ADULT.value: EligibilityIndex(
        policy_details="I confirmed this rider’s identity using a government-issued ID and verified they are age 65 or older."
    ),
    SystemName.MEDICARE.value: EligibilityIndex(
        policy_details="I confirmed this rider’s identity using a government-issued ID and verified they possess a valid "
        "Medicare card."
    ),
    SystemName.COURTESY_CARD.value: EligibilityIndex(
        policy_details="I confirmed this rider’s identity using a government-issued ID and verified they possess an MST "
        "Courtesy Card."
    ),
}
