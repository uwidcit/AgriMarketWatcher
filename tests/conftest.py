import json
import logging
from unittest import mock

import pytest
from fakeredis import FakeStrictRedis


@pytest.fixture()
def all_crop_records() -> dict:
    with open("./data/crop_records.json") as fp:
        return json.load(fp)


@pytest.fixture()
def daily_crop_records(all_crop_records):
    return all_crop_records["daily"]


@pytest.fixture()
def daily_fish_records():
    with open("./data/fish_records.json") as fp:
        return json.load(fp)


@pytest.fixture(scope="session")
def mocked_redis_instance():
    return FakeStrictRedis()


@pytest.fixture()
def stale_cheaper_daily_crop_records(daily_crop_records):
    old_date_str = "2022-01-04 00:00:00"
    new_crops = []
    for crop in daily_crop_records:
        new_price = crop["price"] - 2 if crop["price"] else crop["price"]
        crop.update({"date": old_date_str, "price": new_price})
        new_crops.append(crop)
    return new_crops


@pytest.fixture()
def stale_cheaper_daily_fish_records(daily_fish_records):
    old_date_str = "2022-01-04 00:00:00"
    new_recs = []
    for rec in daily_fish_records:
        new_price = (
            float(rec["frequent_price"]) - 2
            if rec["frequent_price"]
            else rec["frequent_price"]
        )
        rec.update({"date": old_date_str, "price": new_price})
        new_recs.append(rec)
    return new_recs


@pytest.fixture(scope="session", autouse=True)
def mock_pyfcm_notification():
    logging.info("pyfcm.FCMNotification")
    with mock.patch("pyfcm.FCMNotification") as patched:
        yield patched
