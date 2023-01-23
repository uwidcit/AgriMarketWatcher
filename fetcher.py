import time
from datetime import datetime

import requests
import xlrd
from xlrd import open_workbook

from log_configuration import logger

default_category = "ROOT CROPS"
CATEGORIES = [
    "root crops",
    "condiments and spices",
    "leafy vegetables",
    "vegetables",
    "fruits",
    "citrus",
]
MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

base_monthly_url = "https://www.namistt.com/DocumentLibrary/Market%20Reports/Monthly/"
daily_base_url = "https://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-"  # noqa: E501


# Extracts the data from a row and returns a dictionary
# @param sheet : the sheet to be processed
# @param row : the row number to be processed
# @param category : the category of the crop the be considered
# @return : a dictionary representing the data at the specified row
#           for a particular sheet


def process_daily(sheet, row, category):
    dic = {
        "commodity": sheet.cell_value(row, 0)
        .encode(encoding="UTF-8", errors="ignore")
        .decode()
        .lower(),
        "category": category,
        "unit": sheet.cell_value(row, 1)
        .encode(encoding="UTF-8", errors="ignore")
        .decode()
        .lower(),
        "volume": sheet.cell_value(row, 3),
        "price": sheet.cell_value(row, 6),
    }

    if (
        sheet.cell(row, 3) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
        or dic["volume"] == ""
    ):
        dic["volume"] = 0.0

    if (
        sheet.cell(row, 6) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
        or dic["price"] == ""
    ):
        dic["price"] = 0.0

    return dic


def process_row(sheet, row, type):
    global default_category
    global CATEGORIES
    # ensure that the row is not empty
    if sheet.cell_type(row, 0) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        return None
    else:
        # Check if the second column is empty then usually for the category listing
        if not sheet.cell(row, 1).value:
            val = (
                sheet.cell(row, 0)
                .value.encode(encoding="UTF-8", errors="ignore")
                .decode()
                .lower()
            )
            # Check if in the valid list of categories
            if val in CATEGORIES:
                default_category = val
        else:
            if type == "daily":
                return process_daily(sheet, row, default_category)
            else:
                return []


def traverse_workbook(url, workbook_type="daily"):
    values = []
    try:
        data = requests.get(url).content
        wb = open_workbook(url, file_contents=data)
        for s in wb.sheets():
            for row in range(s.nrows):
                if workbook_type == "daily" and row > 10:
                    rowData = process_row(s, row, workbook_type)
                    if rowData:
                        values.append(rowData)
        return values
    except Exception as e:
        logger.error("Error traversing workbook: {0}".format(e))
        return None


def get_url(base_url, year, month, day=None):
    if str(month).isdigit():
        mStr = MONTHS[int(month) - 1]
    else:
        mStr = month
        MONTHS.index(month) + 1

    if day:
        possible_urls = [
            base_url + "%20" + str(day) + "%20" + mStr + "%20" + str(year) + ".xls",
            base_url + str(day) + "%20" + mStr + "%20" + str(year) + ".xls",
        ]
        for url in possible_urls:
            if check_if_url_is_valid(url):
                return url
    else:
        url = base_url + str(mStr) + "%20" + str(year) + "%20NWM%20Monthly%20Report.xls"
        if check_if_url_is_valid(url):
            return url
    return None


def check_if_url_is_valid(url):
    status = requests.head(url).status_code
    return status == 200 or status == 304


def retrieve_daily(base_url, day, month, year):
    if not str(month).isdigit():
        month = MONTHS.index(month) + 1

    url = get_url(base_url, year, month, day)
    if url:
        result = traverse_workbook(url)
        if result:
            # Add the date to each record
            for x in result:
                if x:
                    x.update({"date": datetime(int(year), int(month), int(day))})
                else:
                    result.remove(x)
            return result
        else:
            logger.error("Unable to extract data from the excel file")
    else:
        logger.debug("No Daily report found for: {0}-{1}-{2}".format(day, month, year))
    return None


# Logs sheets that have just been processed into the database
def log_sheet_as_processed(db, sheet):
    db.processed.insert({"url": sheet})


def get_most_recent():
    try:
        day = int(time.strftime("%d"))
        month_num = int(time.strftime("%m"))
        months_names = []
        # Calculate the months needed
        if month_num == 1:
            months_names.extend(MONTHS)
        else:
            months_names.extend(MONTHS[0:month_num])

        year_number = int(time.strftime("%Y"))
        years = [year_number]
        if month_num == 1:
            years.append(year_number - 1)

        reset_daily = False

        # get most recent daily data
        d = None
        for year in years:
            for day in reversed(list(range(day + 1))):
                d = retrieve_daily(daily_base_url, str(day), month_num, str(year))
                if d:
                    logger.info(
                        "Found {0} records for day {1}-{2}-{3}".format(
                            len(d), day, month_num, year
                        )
                    )
                    reset_daily = True
                    break
                elif day < 10:
                    # To accommodate for the possibility of 01, 02 ... 09 as well
                    str_day = "0" + str(day)
                    d = retrieve_daily(daily_base_url, str_day, month_num, str(year))
                    if d:
                        logger.info(
                            "Found {0} records for day {1}-{2}-{3}".format(
                                len(d), day, month_num, year
                            )
                        )
                        reset_daily = True
                        break
            if reset_daily:
                break
            day = int(time.strftime("%d"))
        return {"daily": d}
    except Exception as e:
        logger.error(e)
    finally:
        pass
    return None


def process_run_get_day(day, month, year):
    # extract daily reports
    logger.info("Attempting to retrieve day {0}-{1}-{2}".format(day, month, year))
    d = retrieve_daily(daily_base_url, str(day), month, str(year))
    if d:
        logger.info("Data for {0}-{1}-{2} was successful".format(day, month, year))
    else:
        logger.error("Data for {0}-{1}-{2} was unsuccessful".format(day, month, year))
    return d


def run_get_all(store_data, years, months):
    from models import store_most_recent_daily

    most_recent_daily = None
    daily = []
    reset_daily = False

    for year in reversed(list(years)):  # TODO Update to not have to set date
        for month in reversed(list(months)):  # extract monthly reports
            # extract daily reports
            for day in range(31, 0, -1):
                d = retrieve_daily(daily_base_url, str(day), month, str(year))
                if d:
                    reset_daily = True
                    daily.extend(d)
                    if not most_recent_daily:
                        most_recent_daily = d

    if store_data:
        try:
            # If we have a new set of data for the daily information,
            # we write that into the database
            if reset_daily:
                logger.info("Retrieving the Most Recent Daily Crops")
                store_most_recent_daily(most_recent_daily)

        except Exception as e:
            logger.error(e)

    return {
        "daily": daily,
        "most_recent_daily": most_recent_daily,
    }


if __name__ == "__main__":
    import json

    # from pprint import pprint

    records = get_most_recent()
    # pprint(records)
    print(json.dumps(records, indent=4, default=str))
    with open("./data/records.json", "w") as fp:
        json.dump(obj=records, fp=fp, indent=4, default=str)
