"""Used to set the environment-related variables at runtime (rather than build
time) so that all the necessary pipeline variables are available."""

import os
import sys

REASON = os.environ["REASON"]
# the name of the variable that Azure Pipelines uses for the source branch
# depends on the type of run, so need to check both
SOURCE = os.environ.get("OTHER_SOURCE") or os.environ["INDIVIDUAL_SOURCE"]
TARGET = os.environ["TARGET"]

# the branches that correspond to environments
ENV_BRANCHES = ["dev", "test", "prod"]

if REASON == "PullRequest" and TARGET in ENV_BRANCHES:
    # it's a pull request against one of the environment branches, so use the
    # target branch
    environment = TARGET
elif REASON in ["IndividualCI", "Manual"] and SOURCE in ENV_BRANCHES:
    # it's being run on one of the environment branches, so use that
    environment = SOURCE
else:
    # default to running against dev
    environment = "dev"

# matching logic in ../init.sh
workspace = "default" if environment == "prod" else environment

service_connection = "Production" if environment == "prod" else "Development"

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
print(f"##vso[task.setvariable variable=service_connection;isOutput=true]{service_connection}")
