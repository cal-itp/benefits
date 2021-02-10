#!/usr/bin/env python
"""Simple healthcheck to see if localhost is responding."""
import requests


def main():
    try:
        return requests.get("http://localhost").status_code == 200
    except:
        return False


if __name__ == '__main__':
    main()