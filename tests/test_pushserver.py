from unittest.mock import MagicMock, patch


@patch("redis.StrictRedis")
@patch("requests.get")
@patch("requests.head")
def test_run_for_only_crops_saves_crop_changes(
    mock_head, mocked_get, mock_redis, mock_pyfcm_notification, mocked_redis_instance
):
    with open(
        "tests/data/Norris_Deonarine_NWM_Daily_Market_Report-28_February_2023.xls", "rb"
    ) as f:
        mocked_get.return_value = MagicMock(status_code=201, content=f.read())
        mock_head.return_value = MagicMock(status_code=200)

    # StrictRedis mock return_values is set as above mock_redis_method.
    mock_redis.return_value = mocked_redis_instance

    from models import get_most_recent_daily
    from pushserver import run

    run_result_dict = run(
        notify=False,
        retrieve_crops=True,
        retrieve_fish=False,
        override=True,
    )

    crop_result = run_result_dict["crops"]
    assert len(crop_result) == 77
    assert len(run_result_dict["fish"]) == 0

    records_stored = get_most_recent_daily()
    assert len(records_stored) == len(crop_result)


@patch("redis.StrictRedis")
@patch("requests.get")
@patch("requests.head")
def test_run_for_only_crops_calls_notify_when_price_changes(
    mock_head,
    mocked_get,
    mock_redis,
    mocked_redis_instance,
    stale_cheaper_daily_crop_records,
    mock_pyfcm_notification,
):
    with open(
        "tests/data/Norris_Deonarine_NWM_Daily_Market_Report-28_February_2023.xls", "rb"
    ) as f:
        mocked_get.return_value = MagicMock(status_code=201, content=f.read())
        mock_head.return_value = MagicMock(status_code=200)

        # StrictRedis mock return_values is set as above mock_redis_method.
        mock_redis.return_value = mocked_redis_instance

        # Set some existing values to the database to compare prices

        from models import store_most_recent_daily, get_most_recent_daily
        from pushserver import run

        store_most_recent_daily(crop_records=stale_cheaper_daily_crop_records)

        run_result_dict = run(
            notify=True,
            retrieve_crops=True,
            retrieve_fish=False,
            override=True,
        )

        crop_result = run_result_dict["crops"]
        most_recent = get_most_recent_daily()
        assert len(crop_result) == len(most_recent)
        assert len(crop_result) > 0 and len(most_recent) > 0
        assert most_recent[0]["date"] != "2022-01-04 00:00:00"

        print(mock_pyfcm_notification.call_count)
        assert mock_pyfcm_notification.call_count > 0


@patch("redis.StrictRedis")
@patch("requests.get")
@patch("requests.head")
def test_run_for_only_fishes_call_notif_when_price_changes(
    mock_head,
    mocked_get,
    mock_redis,
    mocked_redis_instance,
    stale_cheaper_daily_fish_records,
    mock_pyfcm_notification,
):
    with open("./tests/data/Daily_POSWFM_27_February_2023.xls", "rb") as f:
        mocked_get.return_value = MagicMock(status_code=201, content=f.read())
        mock_head.return_value = MagicMock(status_code=200)

        # StrictRedis mock return_values is set as above mock_redis_method.
        mock_redis.return_value = mocked_redis_instance

        # Set some existing values to the database to compare prices

        from models import store_most_recent_daily_fish, get_most_recent_daily_fish
        from pushserver import run

        store_most_recent_daily_fish(recent_records=stale_cheaper_daily_fish_records)

        run_result_dict = run(
            notify=False,
            retrieve_crops=False,
            retrieve_fish=True,
            override=True,
        )

        run_result = run_result_dict["fish"]
        most_recent = get_most_recent_daily_fish()
        assert len(run_result) == len(most_recent)
        assert len(run_result) > 0 and len(most_recent) > 0
        assert most_recent[0]["date"] != "2022-01-04 00:00:00"

        assert mock_pyfcm_notification.call_count > 0
