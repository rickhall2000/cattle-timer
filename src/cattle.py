"""This project will download all reports from a cattle auction and return
    them in some sort of useful format"""
import re
import requests
from bs4 import BeautifulSoup

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
    name, data = table
    if data[0] == '\xa0Wt\xa0Range\xa0\xa0\xa0Avg\xa0Wt\xa0\xa0\xa0\xa0Price\xa0Range\xa0\xa0\xa0Avg\xa0Price':
        return table
    else:
        return None

def parse(page_html):
    """Extract the part of the page I care about

    arbuments: page_html - string containing the html to be parsed

    returns: the results, format tbd

    """
    soup = BeautifulSoup(page_html, 'html.parser')
    all_tables = find_table(list(soup.pre.children))
    cleaned_tables = map(convert_table, all_tables)
    just_tables = filter(lambda x: x is not None, cleaned_tables)

    for name, table in just_tables:
        print("***************")
        print(name)
        for line in table:
            print(line)


def download_history_for_marketplace(market_code="TV_LS149"):
    """This returns all available data for a marketplace
    Arguments: market_place code

    Returns: TBD
    """
    header_page = get_report_from_url(market_code)
    reports_available = get_report_dates_from_html(header_page)
    full_results = []
    page_1_result = parse(header_page)
    full_results.append(page_1_result)
    return full_results

def tst():
    """Something easy to call"""
    return download_history_for_marketplace()

def main():
    """For now this is just for testing purposes
    """
    results = download_history_for_marketplace()
#    page_one = results[0]
#    all_lines = page_one.splitlines()
#    print(all_lines[0])

    #print(results)

if __name__ == '__main__':
    main()



# Given the URL for a site, find it's archives

# Current Lanier report: https://www.cattle.com/markets/barn_report.aspx?code=TV_LS149

# Page with archives: https://www.cattle.com/markets/archive.aspx?code=TV_LS149

# Last week: https://www.cattle.com/markets/archive.aspx?code=TV_LS149&date=2019-03-20

# This week: https://www.cattle.com/markets/archive.aspx?code=TV_LS149&date=2019-03-27

# Looks like a date that doesn't exist gets current data


# looks like each category starts iwth \xa0 -- no break space

# >>> b[39]
# '\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0Slaughter\xa0Cows\xa0Boner\xa080-85%'
# >>> b[40]
# <br/>
# >>> b[41]
# '\xa0Wt\xa0Range\xa0\xa0\xa0Avg\xa0Wt\xa0\xa0\xa0\xa0Price\xa0Range\xa0\xa0\xa0Avg\xa0Price'
# >>> b[42]
# <br/>
# >>> b[43]
# '\xa01000-1100\xa0\xa0\xa01050\xa0\xa0\xa0\xa0\xa050.00-54.00\xa0\xa0\xa0\xa0\xa0\xa0\xa051.90'
# >>> b[44]
# <br/>
# >>> b[45]
# '\xa01235-1390\xa0\xa0\xa01318\xa0\xa0\xa0\xa0\xa050.00-51.00\xa0\xa0\xa0\xa0\xa0\xa0\xa050.34'



# >>> b[39]
# '\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0Slaughter\xa0Cows\xa0Boner\xa080-85%'
# >>> b[40]
# <br/>
# >>> b[41]
# '\xa0Wt\xa0Range\xa0\xa0\xa0Avg\xa0Wt\xa0\xa0\xa0\xa0Price\xa0Range\xa0\xa0\xa0Avg\xa0Price'
# >>> b[42]
# <br/>
# >>> b[43]
# '\xa01000-1100\xa0\xa0\xa01050\xa0\xa0\xa0\xa0\xa050.00-54.00\xa0\xa0\xa0\xa0\xa0\xa0\xa051.90'
# >>> b[44]
# <br/>
# >>> b[45]
# '\xa01235-1390\xa0\xa0\xa01318\xa0\xa0\xa0\xa0\xa050.00-51.00\xa0\xa0\xa0\xa0\xa0\xa0\xa050.34'
# >>> b[46]
# <br/>
# >>> b[47]
# '\xa01335-1350\xa0\xa0\xa01342\xa0\xa0\xa0\xa0\xa048.00-49.00\xa0\xa0\xa0\xa0\xa0\xa0\xa048.50\xa0\xa0\xa0Low\xa0Dressing'
# >>> b[48]
# <br/>
# >>> b[49]
# <br/>
# >>> b[50]
# '\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0Slaughter\xa0Cows\xa0Lean\xa085-90%'

