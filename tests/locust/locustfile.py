import random

from locust import HttpUser, constant_pacing, events, task

# Experiment design
# -----------------
#
# User distribution
# https://docs.locust.io/en/stable/writing-a-locustfile.html#weight-and-fixed-count-attributes
# Use weight to uniformly distribute users across all agencies
# SingleAgencyUser gets 75% of the total users (3/4, weight=3)
#  mst, sbmtd, and sacrt split the 75%, each gets 25% of the total site traffic
# RegionalAgencyUser gets 25% of the total users (1/4, weight=1)
#  vctc gets 25% of the total site traffic
#
# Load distribution
# https://docs.locust.io/en/stable/writing-a-locustfile.html#wait-time-attribute
# Pick a target_rate (users/min)
# Pick number_of_concurrent_users (users)
# Calculate the pacing_time (seconds)
# pacing_time = 60 * number_of_concurrent_users / target_rate


class SingleAgencyUser(HttpUser):
    # Weight of 3 so each agency gets 25% of the total site traffic
    weight = 3

    @task
    def complete_entire_flow(self):
        agencies = ["mst", "sbmtd", "sacrt"]
        start_agency = random.choice(agencies)

        response = self.client.get(f"/{start_agency}")

        # (Sequential form steps will go here)
        print(response)


class RegionalAgencyUser(HttpUser):
    # Weight of 1 so the regional agency gets 25% of the total site traffic
    weight = 1

    @task
    def complete_entire_flow(self):
        start_agency = "vctc"

        # STEP 1: Start the journey
        response = self.client.get(f"/{start_agency}")

        # (Sequential form steps will go here)
        print(response)


@events.init_command_line_parser.add_listener
def _(parser):
    # https://docs.locust.io/en/stable/extending-locust.html#custom-arguments
    # Add a custom argument for the target rate
    parser.add_argument("--target-rate", type=float, default=1, help="Target users per minute for dynamic pacing")


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # https://docs.locust.io/en/stable/writing-a-locustfile.html#init
    num_users = environment.parsed_options.num_users
    target_rate = environment.parsed_options.target_rate
    calculated_spawn_rate = target_rate / 60
    environment.parsed_options.spawn_rate = calculated_spawn_rate

    # Calculate the "pacing time" needed to have r users per minute (target rate) running
    pacing_seconds = 60 * num_users / target_rate

    # Print to the console when the test starts
    print("---")
    print(f"Targeting {target_rate} users/min with {num_users} users.")
    print(f"Dynamic Pacing set to {pacing_seconds:.1f} seconds.")
    print("---")

    # Inject the calculated wait time into the User classes
    SingleAgencyUser.wait_time = constant_pacing(pacing_seconds)
    RegionalAgencyUser.wait_time = constant_pacing(pacing_seconds)
