import datetime
import time
import requests
import xlrd
from xlrd import open_workbook

from log_configuration import logger
from app_util import check_if_url_is_valid

months = [
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


def get_url(market, year, month, day=None, with_zero=True):
    base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Daily"
    if str(month).isdigit():
        mStr = months[int(month) - 1]
    else:
        mStr = month
        months.index(month) + 1
    if with_zero:
        day = day if day > 9 else "0{0}".format(day)

    gen_url=f"{base_url}%20{market}%20{day}%20{mStr}%20{year}.xls"
    return (
        base_url
        + "%20"
        + market
        + "%20"
        + str(day)
        + "%20"
        + mStr
        + "%20"
        + str(year)
        + ".xls"
    )


def retrieve_fish_data(daily_fish_url, market, year, month, day):
    records = []
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
                            .encode("ascii")
                            .lower(),
                            "unit": sheet.cell_value(row, 1).encode("ascii").lower(),
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
        logger.error(e)

    return records


def get_most_recent_fish_by_market(market):
    # Get the current day's components
    day = int(time.strftime("%d"))
    month_num = int(time.strftime("%m"))
    year_number = int(time.strftime("%Y"))
    years = [year_number, year_number - 1]
    with_zeros = [True, False]
    try:
        # Loop through all the days of the current month
        for year in years:
            for day in reversed(range(day + 1)):
                for wz in with_zeros:
                    daily_fish_url = get_url(market, year, month_num, day, wz)
                    logger.info(
                        "Retrieving fish for: {0}-{1}-{2} with url {3}".format(
                            day, month_num, year, daily_fish_url
                        )
                    )
                    if check_if_url_is_valid(daily_fish_url):
                        logger.info(
                            f"{daily_fish_url} was valid, attempting to retrieve data"
                        )
                        recs = retrieve_fish_data(
                            daily_fish_url, market, year, month_num, day
                        )
                        return recs  # Fetch the latest value and terminate
    except Exception as e:
        logger.error(e)
        return []


def get_most_recent_fish():
    records = []
    for market in markets:
        market_record = get_most_recent_fish_by_market(market)
        if market_record:
            records = records + market_record
    return records


def eval_url_gens():
    year = 2018
    month_num = 10
    day = 4
    market = markets[1]  # Check different markets
    wz = False  # check different strategy for generating digits in url
    daily_fish_url = get_url(market, year, month_num, day, wz)
    check_url_result = check_if_url_is_valid(daily_fish_url)
    logger.info(check_url_result)
    return check_url_result


if __name__ == "__main__":
    logger.info("Attempting to the test retrieving the fish information")
    logger.info(get_most_recent_fish())
    # evalURLGens()
