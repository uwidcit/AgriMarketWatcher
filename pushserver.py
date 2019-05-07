import fetcher
import fisheries
# import fire
# import predict
import fcm
import sys
import fcm
from pymongo import MongoClient
import datetime
import copy
import logging
logging.StreamHandler(sys.stdout)
# Integrating Sentry
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


sentry_logging = LoggingIntegration(
    level=logging.INFO,        # Capture info and above as breadcrumbs
    event_level=logging.ERROR  # Send no events from log messages
)
sentry_sdk.init(
    dsn="https://7761c2f9313245b496cbbd07ccecceb0@sentry.io/1295927",
    integrations=[sentry_logging]
)

MIN_DIFF = 1.0


def connect2DB():
    try:
        client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
        db = client.get_default_database()
        return db
    except Exception as e:
        print(str(e))
        logging.error("Unable to connect to database: {0}".format(e))
        return None


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
    print("Updating General Dataset")
    db = connect2DB()
    if db:
        if typeR == "daily":
            dateRec = db.daily.find().sort("date", -1).limit(1)
            print("Previous Date: ", dateRec[0]['date'], " Current Date: ", curr['date'])
            print("Current Date " + str(len(curr)))

            if dateRec[0]['date'] != curr['date']:
                db.daily.insert(curr)
                print("from ", dateRec[0]['date'], " to", curr['date'])
        else:  # monthly
            dateRec = db.monthly.find().sort("date", -1).limit(1)
            if dateRec[0]['date'] != curr['date']:
                db.monthly.insert(curr)
                print("from ", dateRec[0]['date'], " to ", curr['date'])


def handleDifference(before, current, typeR="daily"):
    db = connect2DB()
    if before is not None and current is not None:
        print("Before " + before[0]['date'].ctime())
        print("Current " + current[0]['date'].ctime())
        if before[0]['date'].ctime() != current[0]['date'].ctime():
            for b in before:
                for c in current:
                    if b['commodity'] == c['commodity']:
                        if typeR == "daily":
                            if abs(b['price'] - c['price']) > MIN_DIFF:
                                print("price for ", b['commodity'], " changed")
                                # Add new record to the general dataset
                                # updateGeneralDataSet(c, b, typeR)
                                # Send Push notification of change record
                                change = "increased"
                                if b['price'] >= c['price']:
                                    change = "decreased"
                                message = c['commodity'] + " has " + change + " to $" + str(c['price']) + " per " + c['unit']
                                name = b['commodity'].replace(" ", "")
                                fcm.notify(message, name)
                            else:
                                print("price for ", b['commodity'], " remained the same")
                            # Attempt to predict crops (NB disabled for time being)
                            # pred = predict.run(c['commodity'])
                            # if pred != -1:
                            #     newRec = {"name" : c['commodity'], "price" : pred}
                            #     db.predictions.insert(newRec)
                            # breaktypeR

            if typeR == "daily":
                fetcher.storeMostRecentDaily(db, current)
                fetcher.storeDaily(db, current)
                # fire.sendFire(current)
                # fire.sendRecent(current)
            if typeR == "monthly":
                print(current)
                fetcher.storeMostRecentMonthly(db, current)
                fetcher.storeMonthly(db, current)
        else:
            logging.info("no new record found")
    else:
        logging.info("Doesn't exist")


def run():
    logging.info("Executing the Request for retrieval of data on {0}".format(datetime.datetime.now()))
    db = connect2DB()
    if db:
        # Attempt to retrieve Crops Information
        try:
            logging.info("Attempting to retrieve most recent crop data")
            recsCurrent = fetcher.getMostRecent()
            if recsCurrent:
                logging.info("Successfully retrieved crop data")
                handleDifference(list(db.recentMonthly.find()), recsCurrent['monthly'], "monthly")
                handleDifference(list(db.dailyRecent.find()), recsCurrent['daily'], "daily")
            else:
                logging.debug("Unable to successfully retrieve crop data")
        except Exception as e:
            logging.error(e)

        # Attempt to retrieve Fishing Information
        try:
            logging.info("Attempting to retrieve most recent fish data")
            recsFishes = fisheries.getMostRecentFish()
            if recsFishes:
                logging.info("Successfully retrieved fish data")
            else:
                logging.debug("Unable to successfully retrieve fish data")
        except Exception as e:
            logging.error(e)
    else:
        logging.error("Unable to connect to the database")


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

        print(len(recsD))
        print(recsD[0]['price'])
        print(len(recs2))
        print(recs2[0]['price'])

        handleDifference(recsD, recs2)


if __name__ == "__main__":
    print("Attempting To Run the server")
    run()
