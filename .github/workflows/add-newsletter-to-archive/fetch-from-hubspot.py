import argparse
import os
import sys
import urllib
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from hubspot import HubSpot

ACCESS_TOKEN = os.environ["HUBSPOT_ACCESS_TOKEN"]

hubspot = HubSpot(access_token=ACCESS_TOKEN)


def scrape_and_store(url, send_time):
    # scrape HTML
    r = requests.get(url, timeout=30)
    soup = BeautifulSoup(r.content, "html.parser")

    # collect images and store in shared images folder (overwriting any with same filename)
    for img in soup.find_all("img"):
        img_src = img["src"]
        img_src_parsed = urllib.parse.urlsplit(img_src)
        filename = os.path.basename(img_src_parsed.path)

        # download image if we haven't yet
        decoded_filename = urllib.parse.unquote(filename)
        download_path = f"docs/reference/newsletter-archive/exports/images/{decoded_filename}"
        if not Path(download_path).exists():
            print(f"Downloading {decoded_filename} from {img_src_parsed._replace(query='').geturl()}")
            with open(download_path, mode="wb") as file:
                img_url = img_src_parsed._replace(query="").geturl()  # drop query params to get largest size
                img_r = requests.get(img_url, timeout=30)
                file.write(img_r.content)

        # replace original src with relative path and drop responsive attrs
        img["src"] = f"images/{filename}"
        del img["sizes"]
        del img["srcset"]

    newsletter_nicename = send_time.strftime("%B %Y")  # August 2026
    newsletter_slug = send_time.strftime("%Y-%m")  # 2026-08
    newsletter_year = send_time.strftime("%Y")  # August 2026

    # write the updated HTML to a file named YYYY-MM.html
    with open(f"docs/reference/newsletter-archive/exports/{newsletter_slug}.html", "w") as file:
        file.write(str(soup))

    return newsletter_nicename, newsletter_slug, newsletter_year


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="export.py",
        description="Export a HubSpot marketing email's HTML and images, given its ID.",
    )

    parser.add_argument(
        "id",
        type=str,
        help="The HubSpot data type to export (or `all` to get them all).",
    )

    args = parser.parse_args(argv)

    email_response = hubspot.marketing.emails.marketing_emails_api.get_by_id(args.id)
    send_time = email_response.publish_date.astimezone(ZoneInfo("America/Los_Angeles"))
    nicename, slug, year = scrape_and_store(email_response.webversion.url, send_time)

    # If running inside a GitHub Actions environment, store some data for later use.
    if "GITHUB_ENV" in os.environ:
        with open(os.environ["GITHUB_ENV"], "a") as env_file:
            env_file.write(f"NEWSLETTER_NICENAME={nicename}\n")
            env_file.write(f"NEWSLETTER_SLUG={slug}\n")
            env_file.write(f"NEWSLETTER_YEAR={year}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
