"""This project will download all reports from a cattle auction and return
    them in some sort of useful format"""
import re
import requests

MODE = 'dev'

BASE_ADDRESS = "https://www.cattle.com/markets/"
ARCHIVE_BASE = "archive.aspx?code="
MARKET_CODE = "TV_LS149"

ARCHIVE_URL = BASE_ADDRESS + ARCHIVE_BASE + MARKET_CODE

#current_report = "https://www.cattle.com/markets/archive.aspx?code=TV_LS149"
#archive_page = "https://www.cattle.com/markets/archive.aspx?code=TV_LS149"

if MODE == 'dev':
    with open('sample_archive') as f:
        R = f.read()
else:
    R = requests.get(ARCHIVE_URL)


def get_report_urls_from_html(archive_html):
    """Extract the available dates for historical reports from the html of the archive page.

    Arguments: archive_html: a string containing the html from a page containing a list of archives.

    Returns: A list of strings, each containing a datestring in the format
    "2019-03-20" where each match indicates there is a link to a report
    """

    match_string = r'<a href=\"\?code=.+&date=(\d{4}-\d{2}-\d{2})\">'
    return re.findall(match_string, archive_html)

X = get_report_urls_from_html(R)




#print(r.text)

# can do a regex max for <a href="?code=TV_LS149&date=2015-11-18">


# Given the URL for a site, find it's archives

# Current Lanier report: https://www.cattle.com/markets/barn_report.aspx?code=TV_LS149

# Page with archives: https://www.cattle.com/markets/archive.aspx?code=TV_LS149

# Last week: https://www.cattle.com/markets/archive.aspx?code=TV_LS149&date=2019-03-20

# This week: https://www.cattle.com/markets/archive.aspx?code=TV_LS149&date=2019-03-27

# Looks like a date that doesn't exist gets current data
