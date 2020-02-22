from dataManager import connect2DB
import fetcher
import fisheries
import fcm
import sys
import fcm
from pymongo import MongoClient
import datetime
import copy

import sentry_integration
from log_configuration import logger


MIN_DIFF = 1.0


def formatMessage(curr_rec, prev_rec, msg_type="daily"):
    if msg_type == "daily":
        message = {
            'commodity': curr_rec['commodity'],
            'date': curr_rec['date'].strftime('%Y-%m-%dT%H:%M:%S'),
            'price': curr_rec['price'],
            "previous": prev_rec['price']
        }
    else:
        message = {
            'commodity': curr_rec['commodity'],
            'date': curr_rec['date'].strftime('%Y-%m-%dT%H:%M:%S'),
            'mean': curr_rec['mean'],
            "previous": prev_rec['mean']
        }

    return message


def updateGeneralDataSet(curr, prev, typeR="daily"):
    db = connect2DB()
    if db:
        if typeR == "daily":
            dateRec = db.daily.find().sort("date", -1).limit(1)
            logger.info("Previous Date: {0} Current Date: {1}".format(dateRec[0]['date'], curr['date']))
            logger.info("Current Date " + str(len(curr)))

            if dateRec[0]['date'] != curr['date']:
                db.daily.insert(curr)
                logger.info("from {0} to {1}".format(dateRec[0]['date'], curr['date']))
        else:  # monthly
            dateRec = db.monthly.find().sort("date", -1).limit(1)
            if dateRec[0]['date'] != curr['date']:
                db.monthly.insert(curr)
                logger.info("from {0} to {1}".format(dateRec[0]['date'], curr['date']))


def handleDifference(before, current, typeR="daily"):
    db = connect2DB()
    try:
        if before is not None and current is not None:
            logger.info("Before " + before[0]['date'].ctime())
            logger.info("Current " + current[0]['date'].ctime())
            if before[0]['date'].ctime() != current[0]['date'].ctime():
                for b in before:
                    for c in current:
                        if b['commodity'] == c['commodity']:
                            if typeR == "daily":
                                if c['price'] > 0:
                                    if abs(b['price'] - c['price']) > MIN_DIFF:
                                        logger.info("price for {0} changed".format(b['commodity']))
                                        # Add new record to the general dataset
                                        # updateGeneralDataSet(c, b, typeR)
                                        # Send Push notification of change record
                                        change = "increased"
                                        if b['price'] >= c['price']:
                                            change = "decreased"
                                        message = c['commodity'] + " has " + change + \
                                            " to $" + str(c['price']) + \
                                            " per " + c['unit']
                                        name = b['commodity'].replace(" ", "")
                                        fcm.notify(message, name)
                                    else:
                                        logger.info("price for {0} remained the same".format(b['commodity']))

                if typeR == "daily":
                    fetcher.storeMostRecentDaily(db, current)
                    fetcher.storeDaily(db, current)
                if typeR == "monthly":
                    fetcher.storeMostRecentMonthly(db, current)
                    fetcher.storeMonthly(db, current)
            else:
                logger.info("no new record found")
        else:
            logger.info("Doesn't exist")
    except Exception as e:
        logger.error(e)


def run():
    logger.info("Executing the Request for retrieval of data on {0}".format(
        datetime.datetime.now()))
    db = connect2DB()
    if db:
        # Attempt to retrieve Crops Information
        try:
            logger.info("Attempting to retrieve most recent crop data")
            recsCurrent = fetcher.getMostRecent()
            if recsCurrent:
                logger.info("Successfully retrieved crop data")
                handleDifference(list(db.recentMonthly.find()),
                                 recsCurrent['monthly'], "monthly")
                handleDifference(list(db.dailyRecent.find()),
                                 recsCurrent['daily'], "daily")
            else:
                logger.debug("Unable to successfully retrieve crop data")
        except Exception as e:
            logger.error(e)

        # Attempt to retrieve Fishing Information
        try:
            logger.info("Attempting to retrieve most recent fish data")
            recsFishes = fisheries.getMostRecentFish()
            if recsFishes:
                logger.info("Successfully retrieved fish data")
            else:
                logger.debug("Unable to successfully retrieve fish data")
        except Exception as e:
            logger.error(e)
    else:
        logger.error("Unable to connect to the database")


def daily_converter(rec):
    rec['date'] = rec['date'] + datetime.timedelta(days=10)
    rec['price'] += 1
    return rec


def conversionTesting():
    db = connect2DB()
    if db:
        recsD = list(db.dailyRecent.find())
        recs2 = copy.deepcopy(recsD)
        recs2 = list(map(daily_converter, recs2))
        handleDifference(recsD, recs2)


if __name__ == "__main__":
    run()
