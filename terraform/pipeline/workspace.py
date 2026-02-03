"""Used to set the environment-related variables at runtime (rather than build
time) so that all the necessary pipeline variables are available."""

import os
import re
import sys

REASON = os.environ["REASON"]

# the name of the variable that Azure Pipelines uses for the source branch
# depends on the type of run, so need to check both
SOURCE = os.environ.get("OTHER_SOURCE") or os.environ["INDIVIDUAL_SOURCE"]

TARGET = os.environ["TARGET"]
IS_TAG = os.environ["IS_TAG"].lower() == "true"

if REASON == "PullRequest" and TARGET == "main":
    # it's a pull request against main, this is for the dev environment
    environment = "dev"
elif REASON in ["IndividualCI", "Manual"] and SOURCE == "main":
    # it's being run on the main branch, this is for the dev environment
    environment = "dev"
elif REASON in ["IndividualCI"] and IS_TAG and re.fullmatch(r"20\d\d.\d\d.\d+-rc\d+", SOURCE):
    environment = "test"
elif REASON in ["IndividualCI"] and IS_TAG and re.fullmatch(r"20\d\d.\d\d.\d+", SOURCE):
    environment = "prod"
else:
    # default to running against dev
    environment = "dev"

# matching logic in ../init.sh
workspace = "default" if environment == "prod" else environment

service_connection = "Production"

# just for troubleshooting
if TARGET is not None:
    deployment_description = f"from {SOURCE} to {TARGET}"
else:
    deployment_description = f"for {SOURCE}"
print(
    f"Deploying {deployment_description}",
    f"as a result of {REASON}",
    f"using workspace {workspace}," f"and service connection {service_connection}",
    file=sys.stderr,
)

# https://learn.microsoft.com/en-us/azure/devops/pipelines/process/set-variables-scripts?view=azure-devops&tabs=bash#about-tasksetvariable
print(f"##vso[task.setvariable variable=workspace;isOutput=true]{workspace}")
