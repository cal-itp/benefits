#!/usr/bin/env python
"""Simple healthcheck to see if localhost is responding."""
import os
import sys

import requests


def main():
    try:
        ex_code = os.EX_OK if requests.get("http://localhost:8000/healthy").status_code == 200 else os.EX_NOHOST
    except Exception:
        ex_code = os.EX_NOHOST
    sys.exit(ex_code)


if __name__ == '__main__':
    main()