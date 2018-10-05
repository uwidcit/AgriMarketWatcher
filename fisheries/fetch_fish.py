import json
import logging
import urllib2
import xlrd
import time
from xlrd import open_workbook
from pymongo import MongoClient
import datetime

months = ["January", "February",
          "March", "April", "May",
          "June", "July", "August",
          "September", "October",
          "November", "December"]

markets = ['POSWFM', 'OVWFM']


def getCurrentDB():
    try:
        client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
        db = client.get_default_database()
        return db
    except Exception as e:
        logging.error(e)
    return None


def get_url(market, year, month, day=None, with_zero=True):
    base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Daily"
    if str(month).isdigit():
        mStr = months[int(month) - 1]
    else:
        mStr = month
        months.index(month) + 1
    if with_zero:
        day = day if day > 9 else "0{0}".format(day)
    return base_url + "%20" + market + "%20" + str(day) + "%20" + mStr + "%20" + str(year) + ".xls"


def makeHeadRequest(daily_fish_url):
    try:
        request = urllib2.Request(daily_fish_url)
        request.get_method = lambda: 'HEAD'
        response = urllib2.urlopen(request)
        return response.info()
    except Exception as e:
        logging.error(e)
        return None


def retrieveData(daily_fish_url, market, year, month, day):
    records = []
    # Attempt to retrieve records
    try:
        # retrieve the file and open as a stream of data
        data = urllib2.urlopen(daily_fish_url).read()
        wb = open_workbook(daily_fish_url, file_contents=data)
        # For each sheet, check each row for data in specific columns
        for sheet in wb.sheets():
            for row in range(10, sheet.nrows):  # starts at 10, to remove heading rows
                if sheet.cell_type(row, 0) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
                    if sheet.cell_value(row, 0).encode('ascii').lower() != "commodity":
                        cols = {  # Convert row information to a dictionary
                            'commodity': sheet.cell_value(row, 0).encode('ascii').lower(),
                            'unit':  sheet.cell_value(row, 1).encode('ascii').lower(),
                            'min_price': sheet.cell_value(row, 2),
                            'max_price': sheet.cell_value(row, 3),
                            'frequent_price': sheet.cell_value(row, 4),
                            'average_price': sheet.cell_value(row, 5),
                            "volume": sheet.cell_value(row, 6),
                            'date': datetime.datetime(int(year), int(month), int(day)),
                            'market': market
                        }
                        # Set the value to 0 if absent
                        cols['min_price'] = cols['min_price'] if sheet.cell_type(row, 2) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) else 0.0
                        cols['max_price'] = cols['max_price'] if sheet.cell_type(row, 3) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) else 0.0
                        cols['frequent_price'] = cols['frequent_price'] if sheet.cell_type(row, 4) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) else 0.0
                        cols['average_price'] = cols['average_price'] if sheet.cell_type(row, 5) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) else 0.0
                        cols['volume'] = cols['volume'] if sheet.cell_type(row, 6) not in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) else 0.0
                        # Add row record to the collection
                        records.append(cols)
    except Exception as e:
        logging.error(e)

    return records


def getMostRecentFishByMarket(market):
    # Get the current day's components
    day = int(time.strftime("%d"))
    month_num = int(time.strftime("%m"))
    year_number = int(time.strftime("%Y"))
    years = [year_number]
    with_zeros = [True, False]
    try:
        # Loop through all the days of the current month
        for year in years:
            for day in reversed(range(day + 1)):
                for wz in with_zeros:
                    daily_fish_url = get_url(market, year, month_num, day, wz)
                    logging.info("Attempting to retrieve information for: {0}-{1}-{2}".format(day, month_num, year))
                    print("Attempting to retrieve information for: {0}-{1}-{2}".format(day, month_num, year))
                    if makeHeadRequest(daily_fish_url):
                        recs = retrieveData(daily_fish_url, market, year, month_num, day)
                        return recs  # Fetch the latest value and terminate
    except Exception as e:
        logging.error(e)
        return []


def saveMostRecentFish(records):
    # Attempt to save the retrieved records to the database
    try:
        if len(records) > 0:
            logging.info("Retrieve {0} fishing records for today".format(len(records)))
            db = getCurrentDB()
            # Store most recent daily
            db.drop_collection("dailyFishRecent")  # drop as we only need current readings
            db.dailyFishRecent.insert(records)  # Insert recent fish records
            # db.dailyFish.insert(records)  # Insert to the collection of fish records (TODO disabled until we do a better job of handling repeats)
            return True
    except Exception as e:
        logging.error(e)
        return None


def getMostRecentFish():
    records = []
    for market in markets:
        records = records + getMostRecentFishByMarket(market)
    if saveMostRecentFish(records):
        print("{0} fish price records saved successfully".format(len(records)))
    return records


def evalURLGens():
    year = 2018
    month_num = 10
    day = 4
    market = markets[1]  # Check different markets
    wz = False  # check different strategy for generating digits in url
    daily_fish_url = get_url(market, year, month_num, day, wz)
    print(makeHeadRequest(daily_fish_url))


if __name__ == "__main__":
    print("Attempting to the test retrieving the fish information")
    # print(json.dumps(getMostRecentFish(), indent=4)) # datetime is not serializable
    print(getMostRecentFish())
    # evalURLGens()
