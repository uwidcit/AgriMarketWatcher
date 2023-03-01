from datetime import datetime
from typing import Callable

import fcm
import fetcher
from app_util import (
    is_production,
    retrieve_crop_flag_from_env,
    retrieve_fish_flag_from_env,
)
from fetch_fish import get_most_recent_fish
from log_configuration import logger
from models import (
    get_most_recent_daily,
    get_most_recent_daily_fish,
    store_daily_fish,
    store_most_recent_daily,
)

MIN_DIFF = 1.0


def notify_if_daily_crop_price_difference(prev_rec, curr_rec):
    notify_if_difference(
        prev_rec=prev_rec,
        curr_rec=curr_rec,
        commodity_key="commodity",
        current_key="price",
        notify_title="AgriPrice",
    )


def notify_if_daily_fish_difference(prev_rec, curr_rec):
    notify_if_difference(
        prev_rec=prev_rec,
        curr_rec=curr_rec,
        commodity_key="commodity",
        current_key="average_price",
        notify_title="Fish Price",
    )


def notify_if_difference(prev_rec, curr_rec, commodity_key, current_key, notify_title):
    commodity = curr_rec[commodity_key]
    curr_price = curr_rec[current_key]
    unit = curr_rec["unit"]

    if abs(prev_rec[current_key] - curr_rec[current_key]) > MIN_DIFF:
        logger.info("price for {0} changed to ".format(commodity))
        # Build message and send push notification of change record
        change = "decreased" if prev_rec[current_key] >= curr_price else "increased"
        message = "{0} has {1} to ${2} per {3}".format(
            commodity, change, curr_price, unit
        )
        name = commodity.replace(" ", "")
        logger.info("Attempting to send message: {0} using Firebase".format(message))
        fcm.notify(message, name, title=notify_title)
    else:
        logger.info("price for {0} remained the same".format(commodity))


def handle_difference(
    previous_recs,
    current_recs,
    record_type,
    notify,
    override,
    update_handler: Callable,
    notify_handler: Callable,
):
    if record_type != "daily":
        raise ValueError("Invalid record type: {0}".format(record_type))

    # We have both previous and current records so we check if they are different
    if previous_recs and current_recs:
        previous_date = datetime.strptime(
            previous_recs[0]["date"], "%Y-%m-%d %H:%M:%S"
        ).ctime()
        current_date = current_recs[0]["date"].ctime()
        logger.info(f"{record_type}-Prev:{previous_date} Curr:{current_date}")

        # If the dates are different then update records
        if previous_date != current_date:
            update_handler(current_recs)
            notify_handler(previous_recs, current_recs, notify)

        # IF the dates are not different, then override or ignore since not change
        elif override:
            update_handler(current_recs)
        else:
            logger.info("no new record found")
    elif current_recs:
        logger.info("We do not have any previous records. Storing all current records")
        update_handler(current_recs)
    else:
        logger.info("Neither previous or current records received")


def handle_difference_crop(
    previous_recs, current_recs, record_type="daily", notify=False, override=False
):
    return handle_difference(
        previous_recs=previous_recs,
        current_recs=current_recs,
        record_type=record_type,
        notify=notify,
        override=override,
        update_handler=_update_daily_crop_records,
        notify_handler=_check_for_notify,
    )


def _update_daily_crop_records(current_recs):
    logger.info("Attempting to store recent daily records")
    records_stored = store_most_recent_daily(current_recs)
    if records_stored:
        logger.info(f"Stored {records_stored} recent daily records")
    else:
        raise Exception("Failed to store records")


def _check_for_notify(previous_recs, current_recs, notify):
    for prev_rec in previous_recs:
        for curr_rec in current_recs:
            if prev_rec["commodity"] == curr_rec["commodity"]:
                if curr_rec["price"] > 0:
                    if notify:
                        notify_if_daily_crop_price_difference(prev_rec, curr_rec)


def _check_for_notify_fish(previous_recs, current_recs, notify):
    for prev_rec in previous_recs:
        for curr_rec in current_recs:
            if prev_rec["commodity"] == curr_rec["commodity"]:
                if curr_rec["average_price"] > 0:
                    logger.info(
                        "[FISH] The crop {0} has a value change for {1}".format(
                            curr_rec["commodity"],
                            curr_rec["average_price"],
                        )
                    )
                    if notify:
                        notify_if_daily_fish_difference(prev_rec, curr_rec)


def handle_difference_fish(
    previous_recs, current_recs, record_type="daily", notify=False, override=False
):
    return handle_difference(
        previous_recs=previous_recs,
        current_recs=current_recs,
        record_type=record_type,
        notify=notify,
        override=override,
        update_handler=store_daily_fish,
        notify_handler=_check_for_notify_fish,
    )


def compare_with_previous_daily_records(daily_records, notify, override):
    last_recent_recs = get_most_recent_daily()
    handle_difference_crop(
        last_recent_recs, daily_records, "daily", notify=notify, override=override
    )


def compare_with_previous_daily_fish_records(daily_records, notify, override):
    last_recent_recs = get_most_recent_daily_fish()
    handle_difference_fish(
        last_recent_recs, daily_records, "daily", notify=notify, override=override
    )


def run(notify=True, retrieve_crops=True, retrieve_fish=True, override=True):
    date_now = datetime.now()
    current_crop_records = []
    current_fish_records = []

    if retrieve_crops:
        try:
            # Attempt to retrieve Crops Information
            logger.info("Attempting to retrieve most recent crop data")
            current_crop_records = fetcher.get_most_recent()
            if current_crop_records:
                compare_with_previous_daily_records(
                    current_crop_records["daily"], notify=notify, override=override
                )
            else:
                logger.debug("Unable to successfully retrieve crop data")
        except Exception as e:
            logger.error(e, exc_info=True)

    if retrieve_fish:
        try:
            # Attempt to retrieve Fishing Information
            logger.info("Requesting fish data on {0}".format(date_now))
            current_fish_records = get_most_recent_fish()
            if current_fish_records:
                logger.info(
                    "Successfully retrieved {} fish records".format(
                        len(current_fish_records)
                    )
                )
                compare_with_previous_daily_fish_records(
                    current_fish_records, notify=notify, override=override
                )
            else:
                logger.debug("Unable to successfully retrieve fish data")
        except Exception as e:
            logger.error(e, exc_info=True)

    return {"crops": current_crop_records, "fish": current_fish_records}


if __name__ == "__main__":
    is_prod = is_production()
    print(f"Attempting to retrieve information with push service. In Prod?: {is_prod}")
    results = run(
        notify=is_production(),
        retrieve_crops=retrieve_crop_flag_from_env(),
        retrieve_fish=retrieve_fish_flag_from_env(),
    )
    from pprint import pprint

    pprint(results)
