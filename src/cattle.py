"""This project will download all reports from a cattle auction and return
    them in some sort of useful format"""
import re
import datetime
import requests
from bs4 import BeautifulSoup
import output

MODE = 'dev'

BASE_ADDRESS = "https://www.cattle.com/markets/"
ARCHIVE_BASE = "archive.aspx?code="

def get_report_from_url(report_url):
    """Get the html from a report URL.

    arguments: The url to download

    returns: a string containing the html of the requested page
    """
    if MODE == 'dev':
        with open('sample_archive') as sample_file:
            results = sample_file.read()
    else:
        results = requests.get(report_url).text

    return results


def get_report_dates_from_html(archive_html):
    """Extract the available dates for historical reports from the html of the archive page.

    Arguments: archive_html: a string containing the html from a page containing a list of archives.

    Returns: A list of strings, each containing a datestring in the format
    "2019-03-20" where each match indicates there is a link to a report
    """

    match_string = r'<a href=\"\?code=.+&date=(\d{4}-\d{2}-\d{2})\">'
    return re.findall(match_string, archive_html)

def make_archive_url(market_code, report_date=None):
    """Return the appropriate URL for the top archive page
    arguments: markeg_code string containing the id of the auction to download
    returns: a string containing the URL to download the top archive page
    """
    target_url = BASE_ADDRESS + ARCHIVE_BASE + market_code
    if report_date:
        target_url = target_url + "&date=" + report_date
    return target_url

def can_be_table_start(elem):
    """accepts an html element determines if it is the
    start of a table.
    """
    return elem.string is not None and elem.string.startswith('\xa0')

def find_table(html_frag):
    """takes in an a string containing an html grament
    returns up to 2 strings: the first is the text corresponding to a table
    the second is the remainder of the string
    """
    active_table = False
    all_tables = []
    current_table = []
    stop_tags = 0

    for frag in html_frag:
        if (not active_table) and (can_be_table_start(frag)):
            stop_tags = 0
            active_table = True
            title = frag
            continue

        if active_table:
            if frag.string is not None:
                current_table.append(frag.string)
                stop_tags = 0
            elif frag.name is not None and frag.name == "br":
                stop_tags += 1

        if stop_tags == 2:
            all_tables.append((title, current_table))
            current_table = []
            active_table = False
            stop_tags = 0

    return all_tables

def convert_table(table):
    """This filters out blocks that don't begin with a table header.
    """
    _, data = table

    if data and data[0] == '\xa0Wt\xa0Range\xa0\xa0\xa0Avg' + \
        '\xa0Wt\xa0\xa0\xa0\xa0Price\xa0Range\xa0\xa0\xa0Avg\xa0Price':
        return table
    return None

def clean_name(name):
    """This removes ugly chars from name"""
    new_name = ""
    for word in name.split('\xa0'):
        if word == "":
            continue
        if new_name:
            new_name += " "
        new_name += word
    return new_name

def parse_table(raw_table):
    """This converts each line of text into an array of values"""
    rows = raw_table[1:]
    table = []

    for row in rows:
        vals = row.split()
        if len(vals) > 4:
            extra = (" ".join(vals[4:]))
        else:
            extra = ""
        clean_row = vals[0:4]
        clean_row.append(extra)
        table.append(clean_row)
    return table


def parse(page_html):
    """Extract the part of the page I care about
    arbuments: page_html - string containing the html to be parsed
    returns: the results, format tbd
    """
    soup = BeautifulSoup(page_html, 'html.parser')
    all_tables = find_table(list(soup.pre.children))
    cleaned_tables = map(convert_table, all_tables)
    just_tables = filter(lambda x: x is not None, cleaned_tables)
    results = []

    for name, table in just_tables:
        results.append((clean_name(name), parse_table(table)))

    return results

def get_latest_report_date():
    """This function returns a date to use as the current report
        It could read it from the master page
        It could wimp out and add 7 days to the latest date we have
        For now, it just puts the current date in a string format
    """
    my_date = datetime.datetime.now().strftime("%Y-%m-%d")
    return my_date

def download_history_for_marketplace(market_code="TV_LS149"):
    """This returns all available data for a marketplace
    Arguments: market_place code
    Returns: TBD
    """
    master_url = make_archive_url(market_code)
    header_page = get_report_from_url(master_url)
    reports_available = get_report_dates_from_html(header_page)
    full_results = []
    page_1_result = parse(header_page)
    current_date = get_latest_report_date()
    full_results.append((current_date, page_1_result))
    for report in reports_available:
        report_url = make_archive_url(market_code, report)
        page = get_report_from_url(report_url)
        page_result = parse(page)
        full_results.append((report, page_result))

    return full_results

def main():
    """For now this is just for testing purposes
    """
    results = download_history_for_marketplace()
    output.output_results(results, True)

if __name__ == '__main__':
    main()
