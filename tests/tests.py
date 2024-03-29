import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath("."))


def test_fetcher_get_most_recent_daily():
    from fetcher import get_most_recent

    results = get_most_recent()
    assert "daily" in results
    assert len(results["daily"]) > 0


def test_fetch_fish_get_most_recent_fish():
    from fetch_fish import get_most_recent_fish

    results = get_most_recent_fish()
    assert len(results) > 0


@patch("pyfcm.FCMNotification")
def test_pushserver_run_gets_crop_and_fish_and_updates_db_daily(mock_fcm_notification):
    import agrinet

    agrinet.app.config["TESTING"] = True
    agrinet.db.create_all()

    from pushserver import run

    results = run(notify=False)
    assert "crops" in results and "fish" in results
    assert len(results["crops"]) > 0, "No crops returned from the run"
    assert len(results["fish"]) > 0, "No crops returned from the run"

    from models import get_daily, get_most_recent_daily, get_most_recent_daily_fish

    crop_recent_records = get_most_recent_daily()
    assert len(crop_recent_records) > 0, "No recent crops found"

    crops_daily_records = get_daily()
    assert len(crops_daily_records) > 0, "No daily crops found"

    fish_recent_records = get_most_recent_daily_fish()
    assert len(fish_recent_records) > 0, "no recent fish found"

    assert mock_fcm_notification.called


def _endpoint_helper(client, endpoint, name):
    res = client.get(endpoint)
    assert res.status_code == 200, f"Unable to retrieve {name}"
    assert len(res.json) > 0, f"Invalid number of {name} received"


def test_crop_daily_endpoints():
    from agrinet import app

    client = app.test_client()

    _endpoint_helper(client, endpoint="/crops/categories", name="crop categories")
    _endpoint_helper(client, endpoint="/crops/daily", name="daily crops")
    _endpoint_helper(client, endpoint="/crops/daily/dates", name="daily crop dates")
    _endpoint_helper(client, endpoint="/crops/daily/recent", name="recent daily crops")
    _endpoint_helper(
        client, endpoint="/crops/daily/category", name="daily crop categories"
    )


def test_fish_endpoints():
    from agrinet import app

    client = app.test_client()

    _endpoint_helper(client, endpoint="/fishes", name="fish names")
    _endpoint_helper(client, endpoint="/fishes/daily/recent", name="daily recent fish")
    _endpoint_helper(client, endpoint="/fishes/markets", name="fish markets")
