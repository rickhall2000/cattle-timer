"""This project will download all reports from a cattle auction and return
    them in some sort of useful format"""
import csv
import re
import requests
from bs4 import BeautifulSoup

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

    for e in html_frag:
        if (not active_table) and (can_be_table_start(e)):
            stop_tags = 0
            active_table = True
            title = e
            continue

        if active_table:
            if e.string is not None:
                current_table.append(e.string)
                stop_tags = 0
            elif e.name is not None and e.name == "br":
                stop_tags += 1

        if stop_tags == 2:
            all_tables.append((title, current_table))
            current_table = []
            active_table = False
            stop_tags = 0

    return all_tables

def convert_table(table):
    """I am sick of docstrings
    """
    _, data = table
    if data[0] == '\xa0Wt\xa0Range\xa0\xa0\xa0Avg\xa0Wt\xa0\xa0\xa0\xa0Price\xa0Range\xa0\xa0\xa0Avg\xa0Price':
        return table
    return None

def clean_name(name):
    "This removes ugly chars from name"
    new_name = ""
    for word in name.split('\xa0'):
        if word == "":
            continue
        if new_name:
            new_name += " "
        new_name += word
    return new_name

def parse_table(raw_table):
    "This converts each line of text into an array of values"
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

def make_filename(report_date, table_name):
    legal_name = table_name.replace("%", "pct")
    return report_date + "-" + "".join(legal_name.split())

def download_history_for_marketplace(market_code="TV_LS149"):
    """This returns all available data for a marketplace
    Arguments: market_place code
    Returns: TBD
    """
    header_page = get_report_from_url(market_code)
    reports_available = get_report_dates_from_html(header_page)
    full_results = []
    page_1_result = parse(header_page)
    full_results.append(("current", page_1_result))
    return full_results

def output_results(results, combine_results = False):
    header = ["Wt Range","Avg Wt", "Price Range", "Avg Price", "Extra"]
    if combine_results:
        header = ["category", "date"] + header
        filename = "complete"
        with open('data/' + filename + '.csv' , 'w') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                quotechar='"', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(header)
            for report_date, tables in results:
                for table_name, data in tables:
                    for row in data:
                        row = [table_name, report_date] + row
                        filewriter.writerow(row)
    else:
        for report_date, tables in results:
            for table_name, data in tables:
                filename = make_filename(report_date, table_name)
                with open('data/' + filename + '.csv' , 'w') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(header)
                    for row in data:
                        filewriter.writerow(row)


def main():
    """For now this is just for testing purposes
    """
    results = download_history_for_marketplace()
    output_results(results, False)

if __name__ == '__main__':
    main()
