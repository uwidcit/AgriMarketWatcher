import json

import pytest


@pytest.fixture()
def all_crop_records() -> dict:
    with open("./data/crop_records.json") as fp:
        return json.load(fp)


@pytest.fixture()
def dail_crop_records(all_crop_records):
    return all_crop_records["daily"]
