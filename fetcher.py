import requests
import xlrd
from datetime import datetime
from xlrd import open_workbook
from functools import partial
import multiprocessing
from multiprocessing import Pool

import json
import time
import datetime
from log_configuration import logger

from models import store_most_recent_daily, store_most_recent_monthly

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

base_monthly_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Monthly/"
daily_base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-"


# Extracts the data from a row and returns a dictionary
# @param sheet : the sheet to be processed
# @param row : the row number to be processed
# @param category : the category of the crop the be considered
# @return : a dictionary representing the data at the specified row
#           for a particular sheet


def process_daily(sheet, row, category):
    dic = {
        "commodity": sheet.cell_value(row, 0).encode("ascii").lower(),
        "category": category.encode("ascii"),
        "unit": sheet.cell_value(row, 1).encode("ascii"),
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


def process_monthly(sheet, row, category):
    dic = {
        "commodity": sheet.cell_value(row, 0).encode("ascii").lower(),
        "category": category.encode("ascii"),
        "unit": str(sheet.cell_value(row, 1)).encode("ascii"),
    }

    if sheet.cell(row, 2) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        dic["min"] = 0.0
    else:
        dic["min"] = sheet.cell_value(row, 2)

    if sheet.cell(row, 3) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        dic["max"] = 0.0
    else:
        dic["max"] = sheet.cell_value(row, 3)

    if sheet.cell(row, 4) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        dic["mode"] = 0.0
    else:
        dic["mode"] = sheet.cell_value(row, 4)

    if sheet.cell(row, 5) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        dic["mean"] = 0.0
    else:
        dic["mean"] = sheet.cell_value(row, 5)

    if sheet.cell(row, 6) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
        dic["volume"] = 0.0
    else:
        dic["volume"] = sheet.cell_value(row, 6)

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
            val = sheet.cell(row, 0).value
            # Check if in the valid list of categories
            if val.lower() in CATEGORIES:
                default_category = val.upper()
        else:
            if type == "daily":
                return process_daily(sheet, row, default_category)
            else:
                return process_monthly(sheet, row, default_category)


def traverse_workbook(url, workbook_type="daily"):
    values = []
    try:
        data = requests.get(url).content
        wb = open_workbook(url, file_contents=data)
        for s in wb.sheets():
            for row in range(s.nrows):
                if (workbook_type == "daily" and row > 10) or (
                    workbook_type == "monthly" and row > 15
                ):
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
    if str(month).isdigit():
        mStr = MONTHS[month - 1]
    else:
        mStr = month
        month = MONTHS.index(month) + 1

    url = get_url(base_url, year, month, day)
    if url:
        result = traverse_workbook(url)
        if result:
            # Add the date to each record
            for x in result:
                if x:
                    x.update(
                        {"date": datetime.datetime(int(year), int(month), int(day))}
                    )
                else:
                    result.remove(x)
            return result
        else:
            logger.error("Unable to extract data from the excel file")
    else:
        logger.debug("No Daily report found for: {0}-{1}-{2}".format(day, month, year))
    return None


def retrieve_monthly(base_url, month, year):
    if str(month).isdigit():
        mStr = MONTHS[month - 1]
    else:
        mStr = month
        month = MONTHS.index(month) + 1

    url = get_url(base_url, year, month)
    if url:
        result = traverse_workbook(url, "monthly")
        if result:
            for x in result:
                if x:
                    x.update({"date": datetime.datetime(int(year), int(month), 1)})
            return result
        else:
            logger.error("Unable to extract data from the excel file")
    else:
        logger.debug("No Monthly report found for: {0}-{1}".format(month, year))
    return None


# Ideas
# Create a document in the MongoDB database that stores the the most recent data in the database separately from
# the rest of the data in addition to loading the the data together with the current data
# we can then simply use the appropriate url to access the most recent data from the MongoDB
# 1.

# To prevent the repeated parsing of xls files, we can store a list of read xls files


# Parses the json returned by mongoDB in the format for url logger and returns a set of urls
def extract_urls_from_json(j_obj):
    data = json.loads(j_obj)
    return data["url"]


# Gets all of the sheets processed so far by the database
def get_processed_sheets(db):
    processed = db.processed.find()
    if not processed:
        return set()
    return set([extract_urls_from_json(x) for x in processed])


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
        reset_monthly = False

        # get most recent monthly data
        m = None
        for year in years:
            for month in reversed(months_names):
                m = retrieve_monthly(base_monthly_url, month, year)
                if m:
                    logger.info(
                        "successfully found {0} monthly prices for {1}-{2}".format(
                            len(m), month, year
                        )
                    )
                    reset_monthly = True
                    break
            if reset_monthly:
                break

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
        return {"monthly": m, "daily": d}

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


def process_run_get_month(month, year):
    # extract monthly reports
    logger.info("Attempting to retrieve month {0} and {1}".format(month, year))
    m = retrieve_monthly(base_monthly_url, month, str(year))
    if m:
        logger.info("Data for {0}-{1} was successful".format(month, year))
    else:
        logger.error("Data for {0}-{1} was unsuccessful".format(month, year))

    days = range(1, 32)
    cpu_count = int(multiprocessing.cpu_count() / 2)
    pool = Pool(processes=cpu_count)
    all_result = pool.map(partial(process_run_get_day, month=month, year=2020), days)
    print("Received {0} records".format(len(all_result)))
    valid_result = [rec for rec in all_result if rec is not None]
    print("Valid results {0} received".format(len(valid_result)))
    return m, valid_result


def run_get_all(store_data, years, months):
    most_recent_daily = None
    most_recent_monthly = None
    daily = []
    monthly = []
    reset_daily = False
    reset_monthly = False

    for year in reversed(list(years)):  # TODO Update to not have to set date
        for month in reversed(list(months)):  # extract monthly reports
            m = retrieve_monthly(base_monthly_url, month, str(year))
            if m:
                reset_monthly = True
                monthly.extend(m)
                if not most_recent_monthly:
                    most_recent_monthly = m

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
            # If we have a new set of data for the daily information, we insert that into the database
            if reset_daily:
                logger.info("Retrieving the Most Recent Daily Crops")
                store_most_recent_daily(most_recent_daily)

            # If we have a new set of monthly data, we write that to the database
            if reset_monthly:
                logger.info("Retrieving the Most Recent Monthly Crops")
                store_most_recent_monthly(most_recent_monthly)

        except Exception as e:
            logger.error(e)

    return {
        "monthly": monthly,
        "daily": daily,
        "most_recent_monthly": most_recent_monthly,
        "most_recent_daily": most_recent_daily,
    }


if __name__ == "__main__":
    from datetime import date

    # today = date.today()
    # test_year = int(today.strftime("%Y"))
    # result = run_get_all(True, range(test_year - 4, test_year), [today.strftime("%B")])
    # print(result)
    print(get_most_recent())
