""" This handles ouputting the results as a csv file
"""
import csv

def make_filename(report_date, table_name):
    """Used when writing categories as separate files
    Converts a category name to a legal file name.
    """
    legal_name = table_name.replace("%", "pct")
    return report_date + "-" + "".join(legal_name.split())


def output_results(results, combine_results=False):
    """Take combined results, output them into one or many csv files
    """
    header = ["Wt Range", "Avg Wt", "Price Range", "Avg Price", "Extra"]
    if combine_results:
        header = ["category", "date"] + header
        filename = "complete"
        with open('data/' + filename + '.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
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
                with open('data/' + filename + '.csv', 'w') as csvfile:
                    filewriter = csv.writer(csvfile,
                                            delimiter=',',
                                            quotechar='"',
                                            quoting=csv.QUOTE_MINIMAL)
                    filewriter.writerow(header)
                    for row in data:
                        filewriter.writerow(row)
