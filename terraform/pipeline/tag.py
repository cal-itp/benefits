import os
import re

REASON = os.environ["REASON"]
# use variable corresponding to tag triggers
SOURCE = os.environ["INDIVIDUAL_SOURCE"]
IS_TAG = os.environ["IS_TAG"].lower() == "true"

if REASON == "IndividualCI" and IS_TAG:
    if re.fullmatch(r"20\d\d.\d\d.\d+-rc\d+", SOURCE):
        tag_type = "test"
    elif re.fullmatch(r"20\d\d.\d\d.\d+", SOURCE):
        tag_type = "prod"
    else:
        tag_type = None
else:
    tag_type = None

print(tag_type)
