import datetime

import fcm
import fetcher
import fisheries
from log_configuration import logger
from models import (
    get_most_recent_monthly,
    get_most_recent_daily,
    get_most_recent_daily_fish,
    store_most_recent_daily,
    store_most_recent_daily_fish,
    store_daily,
    store_daily_fish,
    store_most_recent_monthly,
    store_monthly,
)

MIN_DIFF = 1.0


def format_message(curr_rec, prev_rec, msg_type="daily"):
    if msg_type == "daily":
        message = {
            "commodity": curr_rec["commodity"],
            "date": curr_rec["date"].strftime("%Y-%m-%dT%H:%M:%S"),
            "price": curr_rec["price"],
            "previous": prev_rec.price,
        }
    else:
        message = {
            "commodity": curr_rec["commodity"],
            "date": curr_rec["date"].strftime("%Y-%m-%dT%H:%M:%S"),
            "mean": curr_rec["mean"],
            "previous": prev_rec.mean,
        }

    return message


def notify_if_daily_crop_price_difference(prev_rec, curr_rec):
    commodity = curr_rec["commodity"]
    curr_price = curr_rec["price"]
    unit = curr_rec["unit"]

    if abs(prev_rec.price - curr_rec["price"]) > MIN_DIFF:
        logger.info("price for {0} changed to ".format(commodity))
        # Build message and send push notification of change record
        change = "decreased" if prev_rec.price >= curr_price else "increased"
        message = "{0} has {1} to ${2} per {3}".format(
            commodity, change, curr_price, unit
        )
        name = commodity.replace(" ", "")
        logger.info("Sending message: {0}".format(message))
        fcm.notify(message, name)
    else:
        logger.info("price for {0} remained the same".format(commodity))


def notify_if_daily_crop_fish_difference(prev_rec, curr_rec):
    commodity = curr_rec["commodity"]
    curr_price = curr_rec["average_price"]
    unit = curr_rec["unit"]

    if abs(prev_rec.average_price - curr_rec["average_price"]) > MIN_DIFF:
        logger.info("price for {0} changed to ".format(commodity))
        # Build message and send push notification of change record
        change = "decreased" if prev_rec.average_price >= curr_price else "increased"
        message = "{0} has {1} to ${2} per {3}".format(
            commodity, change, curr_price, unit
        )
        name = commodity.replace(" ", "")
        logger.info("Sending message: {0}".format(message))
        fcm.notify(message, name)
    else:
        logger.info("price for {0} remained the same".format(commodity))


def handle_difference(previous_recs, current_recs, record_type="daily", notify=False):
    try:
        if previous_recs is not None and current_recs is not None:
            previous_date = previous_recs[0].date.ctime()
            current_date = current_recs[0]["date"].ctime()
            logger.info(
                "Previous: {0} /t Current: {1}".format(previous_date, current_date)
            )
            if previous_date != current_date:
                if record_type == "daily":
                    store_most_recent_daily(current_recs)
                    store_daily(current_recs)
                    for prev_rec in previous_recs:
                        for curr_rec in current_recs:
                            if prev_rec.commodity == curr_rec["commodity"]:
                                if curr_rec["price"] > 0:
                                    if notify:
                                        notify_if_daily_crop_price_difference(
                                            prev_rec, curr_rec
                                        )

                if record_type == "monthly":
                    store_most_recent_monthly(current_recs)
                    store_monthly(current_recs)
            else:
                logger.info("no new record found")
        else:
            logger.info("Doesn't exist")
    except Exception as e:
        logger.error(e)


def handle_difference_fish(
    previous_recs, current_recs, record_type="daily", notify=False
):
    try:
        if previous_recs and current_recs:
            logger.info("[FISH] Received value for both previous rec and curr rec")
            previous_date = previous_recs[0].date.ctime()
            current_date = current_recs[0]["date"].ctime()
            logger.info(
                "Previous: {0} /t Current: {1}".format(previous_date, current_date)
            )
            if previous_date != current_date:
                if record_type == "daily":
                    logger.info("[FISH] Attempting to store most recent records")
                    store_most_recent_daily_fish(current_recs)
                    logger.info("[FISH] Attempting to store daily records")
                    store_daily_fish(current_recs)

                    for prev_rec in previous_recs:
                        for curr_rec in current_recs:
                            if prev_rec.commodity == curr_rec["commodity"]:
                                if curr_rec["average_price"] > 0:
                                    logger.info(
                                        "[FISH] The crop {0} has a value change for {1}".format(
                                            curr_rec["commodity"],
                                            curr_rec["average_price"],
                                        )
                                    )
                                    if notify:
                                        notify_if_daily_crop_fish_difference(
                                            prev_rec, curr_rec
                                        )
                                    else:
                                        logger.info("[FISH] Skipping notification")
            else:
                logger.info("[FISH] no new record found")
        elif not previous_recs:
            logger.info("[FISH] No previous fish records exists")
            logger.info("[FISH] Attempting to store the first most recent records")
            store_most_recent_daily_fish(current_recs)
            logger.info("[FISH] Attempting to store the first daily records")
            store_daily_fish(current_recs)
        else:
            logger.info("[FISH] Doesn't exist")
    except Exception as e:
        logger.error(e)


def compare_with_previous_monthly_records(monthly_records, notify):
    last_recent_recs = get_most_recent_monthly()
    handle_difference(last_recent_recs, monthly_records, "monthly", notify=notify)


def compare_with_previous_daily_records(daily_records, notify):
    last_recent_recs = get_most_recent_daily()
    handle_difference(last_recent_recs, daily_records, "daily", notify=notify)


def compare_with_previous_daily_fish_records(daily_records, notify):
    last_recent_recs = get_most_recent_daily_fish()
    handle_difference_fish(last_recent_recs, daily_records, "daily", notify=notify)


def run(notify=True):
    date_now = datetime.datetime.now()
    logger.info("Requesting crop data on {0}".format(date_now))
    current_crop_records = {"monthly": [], "daily": []}
    current_fish_records = []

    try:
        # Attempt to retrieve Crops Information
        logger.info("Attempting to retrieve most recent crop data")
        current_crop_records = fetcher.get_most_recent()
        if current_crop_records:
            logger.info("Successfully retrieved crop data")
            compare_with_previous_monthly_records(
                current_crop_records["monthly"], notify=notify
            )

            compare_with_previous_daily_records(
                current_crop_records["daily"], notify=notify
            )
        else:
            logger.debug("Unable to successfully retrieve crop data")
    except Exception as e:
        logger.error(e, exc_info=True)

    try:
        # Attempt to retrieve Fishing Information
        logger.info("Requesting fish data on {0}".format(date_now))
        current_fish_records = fisheries.getMostRecentFish()
        if current_fish_records:
            logger.info(
                "Successfully retrieved {} fish records".format(
                    len(current_fish_records)
                )
            )
            compare_with_previous_daily_fish_records(
                current_fish_records, notify=notify
            )
        else:
            logger.debug("Unable to successfully retrieve fish data")
    except Exception as e:
        logger.error(e, exc_info=True)

    return {"crops": current_crop_records, "fish": current_fish_records}


if __name__ == "__main__":
    results = run(notify=False)
    print("Retrieved:")
    #
    # from pprint import pprint
    #
    # pprint(results)
