import os
import subprocess
import sys
from datetime import datetime


def create_annotated_tag(tag_name):
    """Creates a local Git annotated tag."""
    print(f"Creating tag: {tag_name}")
    # Ensure tag doesn't already exist to avoid conflicts
    subprocess.run(["git", "tag", "-d", tag_name], capture_output=True, check=False)

    cmd = ["git", "tag", "-a", tag_name, "-m", "Testing tag"]
    subprocess.run(cmd, capture_output=True, check=True)


def create_env() -> bool:
    """Checks if .env exists, if not, creates one as required by Compose so it doesn't crash"""
    env_file = ".env"
    if not os.path.exists(env_file):
        print(".env file not found. Creating empty .env for testing.")
        with open(env_file, "w"):
            pass
        return True
    return False


def build_and_start_container() -> bool:
    """Builds and starts the client container service."""
    print("Building and starting container")
    created_env = create_env()
    cmd = ["docker", "compose", "up", "-d", "--build", "client"]
    # Set capture_output=False so we can see the build progress
    subprocess.run(cmd, capture_output=False, check=True)
    return created_env


def cleanup(tag_name, created_env):
    """Removes the Git tag and temporary .env file."""
    print("Cleanup")

    # Remove Git tag
    cmd = ["git", "tag", "-d", tag_name]
    subprocess.run(cmd, capture_output=True)
    print(f"Deleted local tag '{tag_name}'")

    # Remove container
    cmd = ["docker", "compose", "down"]
    subprocess.run(cmd, capture_output=False, check=True)

    # Remove .env if we created it
    if created_env:
        if os.path.exists(".env"):
            os.remove(".env")
            print("Deleted temporary .env file")


def get_actual_version():
    """Runs the Docker command to get the version from the running app."""
    cmd = [
        "docker",
        "compose",
        "exec",
        "-T",
        "client",
        "python",
        "manage.py",
        "shell",
        "-c",
        "import benefits; print(benefits.VERSION)",
    ]

    try:
        # Run the Docker command and capture the output
        # Set text=True so that result.stdout is a Python string
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # This ignores the "... objects imported automatically..." banner
        output_lines = result.stdout.strip().splitlines()
        if not output_lines:
            raise ValueError("No output received from Docker command.")

        return output_lines[-1].strip()

    except subprocess.CalledProcessError as e:
        print(f"Error running Docker command: {e.stderr}")
        sys.exit(1)


def normalize_version(version_str):
    """
    Normalizes the Python version to match the Git tag format since
    Python versions normalize single digit months to no leading zeros and
    the Git tag format uses a leading zero for single digit months.
    """
    parts = version_str.split(".")
    if len(parts) >= 2:
        # Left zero-pad the month
        parts[1] = parts[1].zfill(2)
    return ".".join(parts)


def main():
    expected_tag = datetime.now().strftime("%Y.%m.100")
    created_temp_env = False

    try:
        create_annotated_tag(expected_tag)
        created_temp_env = build_and_start_container()

        print("Fetching actual version from the container...")
        actual_raw = get_actual_version()

        # Normalize to match the 'YYYY.MM.Ver' format of the tag
        actual_normalized = normalize_version(actual_raw)

        print(f"Expected tag: {expected_tag}")
        print(f"Actual   tag: {actual_normalized} (Raw Python output: {actual_raw})")

        if actual_normalized == expected_tag:
            print("Success: Version matches git tag.")
            sys.exit(0)
        else:
            print("Error: Version mismatch")
            sys.exit(1)
    finally:
        cleanup(expected_tag, created_temp_env)


if __name__ == "__main__":
    main()
