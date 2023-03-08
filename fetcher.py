import time
from datetime import datetime

import requests
import xlrd
from requests.exceptions import ConnectTimeout
from xlrd import open_workbook

from app_util import check_if_url_is_valid, is_production
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
daily_base_url = "https://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report"  # noqa: E501

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
    data = requests.get(url).content
    wb = open_workbook(url, file_contents=data)
    for s in wb.sheets():
        for row in range(s.nrows):
            if workbook_type == "daily" and row > 10:
                rowData = process_row(s, row, workbook_type)
                if rowData:
                    values.append(rowData)
    return values


def get_url(base_url, year, month, day=None):
    if str(month).isdigit():
        mStr = MONTHS[int(month) - 1]
    else:
        mStr = month

    if day:
        possible_urls = [
            f"{base_url}%20-%20{day}%20{mStr}%20{year}.xls",  # ...Market Report - 6 March 2023.xls
            f"{base_url}%20-%200{day}%20{mStr}%20{year}.xls",  # ...Market Report - 06 March 2023.xls
            f"{base_url}%20-{day}%20{mStr}%20{year}.xls",  # ...Market Report -6 March 2023.xls
            f"{base_url}%20-0{day}%20{mStr}%20{year}.xls",  # ...Market Report -06 March 2023.xls
            f"{base_url}-{day}%20{mStr}%20{year}.xls",  # ...Market Report-6 March 2023.xls
            f"{base_url}-0{day}%20{mStr}%20{year}.xls",  # ...Market Report-06 March 2023.xls
        ]
        for url in possible_urls:
            if check_if_url_is_valid(url):
                return url
    else:
        url = f"{base_url}{mStr}%20{year}%20NWM%20Monthly%20Report.xls"
        if check_if_url_is_valid(url):
            return url
    return None


def retrieve_daily(url, day, month, year):
    result = traverse_workbook(url)
    if month in MONTHS:
        month = MONTHS.index(month) + 1
    if result:
        # Add the date to each record
        for x in result:
            if x:
                x.update({"date": datetime(int(year), int(month), int(day))})
            else:
                result.remove(x)
        return result
    else:
        logger.error(f"Unable to extract data from the excel file: {url}")


# Logs sheets that have just been processed into the database
def log_sheet_as_processed(db, sheet):
    db.processed.insert({"url": sheet})


def valid_url_generator(
    base_url: str = daily_base_url, display_dates: bool = not is_production()
):
    starting_day_num = int(time.strftime("%d"))
    curr_month_num = int(time.strftime("%m"))
    year_num = int(time.strftime("%Y"))

    months_names = []
    # Calculate the months needed
    if curr_month_num == 1:
        months_names.extend(MONTHS)
    else:
        months_names.extend(MONTHS[0:curr_month_num])

    years = [year_num]
    if curr_month_num == 1:
        years.append(year_num - 1)

    # get most recent daily data
    for year in years:
        for month_name in reversed(months_names):
            for day in reversed(list(range(1, starting_day_num + 1))):
                # day_str = f"0{day}" if day < 10 else str(day)
                day_str = str(day)
                daily_crop_url = get_url(base_url, year, month_name, day_str)
                if daily_crop_url:
                    if display_dates:
                        logger.info(
                            f"valid URL {daily_crop_url} for {day_str}-{month_name}"
                        )
                    yield (daily_crop_url, day_str, month_name, year)

            # We're starting a new month so start from the maximum day value
            starting_day_num = 29 if curr_month_num == 2 else 31


def get_most_recent():
    for url_tuple in valid_url_generator():
        try:
            daily_crop_url, day_str, month_name, year = url_tuple
            daily_record = retrieve_daily(
                daily_crop_url, day_str, month_name, str(year)
            )
            if daily_record:
                logger.info(
                    f"Found {len(daily_record)} records {day_str}-{month_name}-{year}"
                )
                return daily_record
        except Exception as e:
            logger.error(f"{e}", exc_info=True)


if __name__ == "__main__":
    import json

    # records = list(valid_url_generator())
    records = get_most_recent()
    print(json.dumps(records, indent=4, default=str))
    # with open("./data/records.json", "w") as fp:
    #     json.dump(obj=records, fp=fp, indent=4, default=str)
