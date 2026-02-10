import subprocess
import sys


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
    if len(sys.argv) < 2:
        print("Usage: python check-dynamic-version.py <expected_tag>")
        sys.exit(1)

    expected_tag = sys.argv[1]

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


if __name__ == "__main__":
    main()
