import json

from agrinet import redis_client
from log_configuration import logger

CROP_DAILY_KEY = "crop_daily"
CROP_COMMODITY_KEY = "crop_commodity"
CROP_CATEGORY_KEY = "crop_category"
FISH_DAILY_KEY = "fish_daily"
FISH_CATEGORY_KEY = "fish_category"


def delete_crop_records():
    redis_client.delete(CROP_DAILY_KEY, CROP_COMMODITY_KEY, CROP_CATEGORY_KEY)


def store_daily(records):
    logger.info("No longer supports anything else by the latest records")
    store_most_recent_daily(records)


def store_most_recent_daily(
    crop_records: list[dict],
    crop_daily_key: str = CROP_DAILY_KEY,
    crop_commodity_key: str = CROP_COMMODITY_KEY,
    crop_category_key: str = CROP_CATEGORY_KEY,
) -> dict:
    try:
        # Not an atomic operation. Failure at any point will leave data inconsistent
        return {
            "crops": store_daily_crops(crop_records, crop_daily_key),
            "category": store_daily_category(crop_records, crop_category_key),
            "commodity": store_daily_commodity(crop_records, crop_commodity_key),
        }
    except Exception as e:
        logger.critical(e, exc_info=True)
    return {}


def store_daily_crops(crop_records: list, crop_daily_key: str = CROP_DAILY_KEY) -> int:
    for crop in crop_records:
        crop["date"] = str(crop["date"])
    redis_client.set(crop_daily_key, json.dumps(crop_records))
    return len(crop_records)


def store_daily_commodity(
    crop_records: list, crop_commodity_key: str = CROP_COMMODITY_KEY
) -> int:
    commodities = list({crop["commodity"] for crop in crop_records})
    redis_client.set(crop_commodity_key, json.dumps(commodities))
    return len(commodities)


def get_most_recent_daily(crop_daily_key: str = CROP_DAILY_KEY):
    commodities_str = redis_client.get(crop_daily_key)
    return json.loads(commodities_str or "[]")


def get_daily_by_id(rec_id):
    daily_crops = get_most_recent_daily()
    return daily_crops[rec_id]


def store_daily_category(
    crop_records: list, crop_category_key: str = CROP_CATEGORY_KEY
) -> int:
    categories = list({crop["category"] for crop in crop_records})
    redis_client.set(crop_category_key, json.dumps(categories))
    return len(categories)


def get_distinct_commodity(crop_commodity_key: str = CROP_COMMODITY_KEY) -> list[str]:
    commodities_str = redis_client.get(crop_commodity_key)
    return json.loads(commodities_str or "[]")


def get_distinct_categories(crop_category_key: str = CROP_CATEGORY_KEY) -> list[str]:
    categories_str = redis_client.get(crop_category_key)
    return json.loads(categories_str or "[]")


def get_distinct_commodity_by_category(category):
    daily_crops = get_most_recent_daily()
    return [crop for crop in daily_crops if crop["category"] == category.lower()]


def get_daily_recent_by_commodity(commodity):
    daily_crops = get_most_recent_daily()
    return [crop for crop in daily_crops if crop["commodity"] == commodity.lower()]


def get_daily():
    return get_most_recent_daily()


# ***** FISH ****


def get_distinct_fish_commodity():
    commodities = get_most_recent_daily_fish()
    return list({commodity["commodity"] for commodity in commodities})


def get_most_recent_daily_fish():
    commodities_str = redis_client.get(FISH_DAILY_KEY)
    return json.loads(commodities_str or "[]")


def store_daily_fish(records):
    return store_most_recent_daily_fish(records)


def store_most_recent_daily_fish(recent_records):
    redis_client.set(FISH_DAILY_KEY, json.dumps(recent_records))
    return len(recent_records)


def get_daily_recent_by_commodity_fish(commodity):
    commodities = get_most_recent_daily_fish()
    return [
        commodity
        for commodity in commodities
        if commodity["commodity"] == commodity.lower()
    ]
