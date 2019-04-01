"""This project will download all reports from a cattle auction and return
    them in some sort of useful format"""
import re
import requests

MODE = 'dev'

BASE_ADDRESS = "https://www.cattle.com/markets/"
ARCHIVE_BASE = "archive.aspx?code="


#current_report = "https://www.cattle.com/markets/archive.aspx?code=TV_LS149"
#archive_page = "https://www.cattle.com/markets/archive.aspx?code=TV_LS149"


def get_report_from_url(report_url):
    """Get the html from a report URL.

    arguments: The url to download

    returns: a string containing the html of the requested page
    """

    if MODE == 'dev':
        with open('sample_archive') as sample_file:
            results = sample_file.read()
    else:
        results = requests.get(report_url)

    return results


def get_report_dates_from_html(archive_html):
    """Extract the available dates for historical reports from the html of the archive page.

    Arguments: archive_html: a string containing the html from a page containing a list of archives.

    Returns: A list of strings, each containing a datestring in the format
    "2019-03-20" where each match indicates there is a link to a report
    """

    match_string = r'<a href=\"\?code=.+&date=(\d{4}-\d{2}-\d{2})\">'
    return re.findall(match_string, archive_html)

def make_archive_head_url(market_code):
    """Return the appropriate URL for the top archive page
    arguments: markeg_code string containing the id of the auction to download
    returns: a string containing the URL to download the top archive page
    """
    return BASE_ADDRESS + ARCHIVE_BASE + market_code


def download_history_for_marketplace(market_code="TV_LS149"):
    """This returns all available data for a marketplace
    Arguments: market_place code

    Returns: TBD
    """
    header_page = get_report_from_url(market_code)
    reports_available = get_report_dates_from_html(header_page)
    return reports_available



# Given the URL for a site, find it's archives

# Current Lanier report: https://www.cattle.com/markets/barn_report.aspx?code=TV_LS149

# Page with archives: https://www.cattle.com/markets/archive.aspx?code=TV_LS149

# Last week: https://www.cattle.com/markets/archive.aspx?code=TV_LS149&date=2019-03-20

# This week: https://www.cattle.com/markets/archive.aspx?code=TV_LS149&date=2019-03-27

# Looks like a date that doesn't exist gets current data
