import datetime
import time

import requests
import xlrd
from xlrd import open_workbook

from app_util import check_if_url_is_valid
from log_configuration import logger

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

markets = ["POSWFM", "OVWFM"]


def get_fish_market_url(market, year, month, day=None, with_zero=True):
    base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Daily"
    if str(month).isdigit():
        mStr = MONTHS[int(month) - 1]
    else:
        mStr = month

    return f"{base_url}%20{market}%20{day}%20{mStr}%20{year}.xls"


def retrieve_fish_data(daily_fish_url, market, year, month, day):
    records = []
    if month in MONTHS:
        month = MONTHS.index(month) + 1

    # Attempt to retrieve records
    try:
        # retrieve the file and open as a stream of data
        data = requests.get(daily_fish_url).content
        wb = open_workbook(daily_fish_url, file_contents=data)
        # For each sheet, check each row for data in specific columns
        for sheet in wb.sheets():
            for row in range(10, sheet.nrows):  # starts at 10, to remove heading rows
                if sheet.cell_type(row, 0) not in (
                    xlrd.XL_CELL_EMPTY,
                    xlrd.XL_CELL_BLANK,
                ):
                    if sheet.cell_value(row, 0).encode("ascii").lower() != "commodity":
                        cols = {  # Convert row information to a dictionary
                            "commodity": sheet.cell_value(row, 0)
                            .encode(encoding="UTF-8", errors="ignore")
                            .decode()
                            .lower(),
                            "unit": sheet.cell_value(row, 1)
                            .encode(encoding="UTF-8", errors="ignore")
                            .decode()
                            .lower(),
                            "min_price": sheet.cell_value(row, 2),
                            "max_price": sheet.cell_value(row, 3),
                            "frequent_price": sheet.cell_value(row, 4),
                            "average_price": sheet.cell_value(row, 5),
                            "volume": sheet.cell_value(row, 6),
                            "date": datetime.datetime(int(year), int(month), int(day)),
                            "market": market,
                        }
                        # Set the value to 0 if absent
                        cols["min_price"] = (
                            cols["min_price"]
                            if sheet.cell_type(row, 2)
                            not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                            else 0.0
                        )
                        cols["max_price"] = (
                            cols["max_price"]
                            if sheet.cell_type(row, 3)
                            not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                            else 0.0
                        )
                        cols["frequent_price"] = (
                            cols["frequent_price"]
                            if sheet.cell_type(row, 4)
                            not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                            else 0.0
                        )
                        cols["average_price"] = (
                            cols["average_price"]
                            if sheet.cell_type(row, 5)
                            not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                            else 0.0
                        )
                        cols["volume"] = (
                            cols["volume"]
                            if sheet.cell_type(row, 6)
                            not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                            else 0.0
                        )
                        # Add row record to the collection
                        records.append(cols)
    except Exception as e:
        logger.error(e, exc_info=True)

    return records


def get_most_recent_fish_by_market(market):
    # Get the current day's components
    starting_day = int(time.strftime("%d"))
    curr_month_num = int(time.strftime("%m"))
    months_names = []
    # Calculate the months needed
    if curr_month_num == 1:
        months_names.extend(MONTHS)
    else:
        months_names.extend(MONTHS[0:curr_month_num])

    year_number = int(time.strftime("%Y"))
    years = [year_number]
    if curr_month_num == 1:
        years.append(year_number - 1)

    # Loop through all the days of the current month
    for year in years:
        for month_name in reversed(months_names):
            for day in reversed(list(range(starting_day + 1))):
                try:
                    day_str = f"0{day}" if day < 10 else str(day)
                    daily_fish_url = get_fish_market_url(
                        market, year, month_name, day_str
                    )
                    logger.info(f"URL {daily_fish_url} for {day_str}-{month_name}")
                    if check_if_url_is_valid(daily_fish_url):
                        logger.info(f"Attempting to retrieve data for {daily_fish_url}")
                        recs = retrieve_fish_data(
                            daily_fish_url, market, year, month_name, day
                        )
                        logger.info(f"{len(recs)}")
                        if recs:
                            return recs  # Fetch the latest value and terminate
                        else:
                            logger.info(f"Failed to parse {day}-{month_name}-{year}")
                except requests.ConnectTimeout:
                    logger.info(f"No record for {day}-{month_name}-{year}")
                except Exception as e:
                    logger.error(f"{e}", exc_info=True)

            # We're starting a new month so start from the maximum day value
            starting_day = 31
    return []


def get_most_recent_fish():
    records = []
    for market in markets:
        market_record = get_most_recent_fish_by_market(market)
        print(market_record)
        if market_record:
            records = records + market_record

    return filter_valid_fish_records(records)


def is_valid_digit(value):
    try:
        float(value)
        return True
    except Exception:
        return False


def filter_valid_fish_records(records):
    new_recs = []
    for rec in records:
        if is_valid_digit(rec["frequent_price"]) and is_valid_digit(rec["volume"]):
            new_recs.append(rec)
    return new_recs


def eval_url_gens():
    year = 2018
    month_num = 10
    day = 4
    market = markets[1]  # Check different markets
    wz = False  # check different strategy for generating digits in url
    daily_fish_url = get_fish_market_url(market, year, month_num, day, wz)
    check_url_result = check_if_url_is_valid(daily_fish_url)
    logger.info(check_url_result)
    return check_url_result


if __name__ == "__main__":
    logger.info("evaluate url generation process: {0}".format(eval_url_gens()))
    logger.info("Attempting to the test retrieving the fish information")
    logger.info(get_most_recent_fish())
