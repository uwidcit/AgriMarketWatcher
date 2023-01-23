from datetime import datetime

import fcm
import fetcher
from app_util import is_production
from log_configuration import logger
from models import (
    get_most_recent_daily,
    get_most_recent_daily_fish,
    store_daily,
    store_daily_fish,
    store_most_recent_daily,
    store_most_recent_daily_fish,
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


def notify_if_daily_fish_difference(prev_rec, curr_rec):
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
        logger.info("Attempting to send message: {0} using Firebase".format(message))
        fcm.notify(message, name, title="Fish Price")
    else:
        logger.info("price for {0} remained the same".format(commodity))


def handle_difference(previous_recs, current_recs, record_type="daily", notify=False):
    try:
        if previous_recs and current_recs:
            previous_date_str = previous_recs[0]["date"]
            previous_date = datetime.strptime(
                previous_date_str, "%Y-%m-%d %H:%M:%S"
            ).ctime()
            current_date = current_recs[0]["date"].ctime()
            logger.info(f"{record_type}-Prev:{previous_date} Curr:{current_date}")

            if previous_date != current_date:
                logger.info(f"we have updated {record_type} crop information")

                if record_type == "daily":
                    _update_daily_crop_records(current_recs)
                    _check_for_notify(previous_recs, current_recs, notify)
                else:
                    logger.error(f"Invalid record type: {record_type}")
            else:
                logger.info("no new record found")
        elif current_recs:
            logger.info(
                "We do not have any previous records. Storing all current records"
            )
            if record_type == "daily":
                _update_daily_crop_records(current_recs)
            else:
                logger.error(f"Invalid record type: {record_type}")
        else:
            logger.info("Neither previous or current records received")
    except Exception as e:
        logger.error(e, exc_info=True)


def _update_daily_crop_records(current_recs):
    logger.info("Attempting to store recent daily records")
    records_stored = store_most_recent_daily(current_recs)
    logger.info(f"Stored {records_stored} recent daily records")

    logger.info("Attempting to store recent daily records")
    records_stored = store_daily(current_recs)
    logger.info(f"Stored {records_stored} recent daily records")


def _check_for_notify(previous_recs, current_recs, notify):
    for prev_rec in previous_recs:
        for curr_rec in current_recs:
            if prev_rec.commodity == curr_rec["commodity"]:
                if curr_rec["price"] > 0:
                    if notify:
                        notify_if_daily_crop_price_difference(prev_rec, curr_rec)


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
                                        notify_if_daily_fish_difference(
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


def compare_with_previous_daily_records(daily_records, notify):
    last_recent_recs = get_most_recent_daily()
    handle_difference(last_recent_recs, daily_records, "daily", notify=notify)


def compare_with_previous_daily_fish_records(daily_records, notify):
    last_recent_recs = get_most_recent_daily_fish()
    handle_difference_fish(last_recent_recs, daily_records, "daily", notify=notify)


def run(notify=True):
    date_now = datetime.now()
    logger.info("Requesting crop data on {0}".format(date_now))
    current_crop_records = {"daily": []}
    current_fish_records = []

    try:
        # Attempt to retrieve Crops Information
        logger.info("Attempting to retrieve most recent crop data")
        current_crop_records = fetcher.get_most_recent()
        if current_crop_records:
            compare_with_previous_daily_records(
                current_crop_records["daily"], notify=notify
            )
        else:
            logger.debug("Unable to successfully retrieve crop data")
    except Exception as e:
        logger.error(e, exc_info=True)

    # try:
    #     # Attempt to retrieve Fishing Information
    #     logger.info("Requesting fish data on {0}".format(date_now))
    #     current_fish_records = get_most_recent_fish()
    #     if current_fish_records:
    #         logger.info(
    #             "Successfully retrieved {} fish records".format(
    #                 len(current_fish_records)
    #             )
    #         )
    #         compare_with_previous_daily_fish_records(
    #             current_fish_records, notify=notify
    #         )
    #     else:
    #         logger.debug("Unable to successfully retrieve fish data")
    # except Exception as e:
    #     logger.error(e, exc_info=True)

    return {"crops": current_crop_records, "fish": current_fish_records}


if __name__ == "__main__":
    is_prod = is_production()
    print(f"Attempting to retrieve information with push service. In Prod?: {is_prod}")
    results = run(notify=is_production())
    # from pprint import pprint
    # pprint(results)
