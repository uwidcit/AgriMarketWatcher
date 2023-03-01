import datetime
from unittest.mock import Mock, patch


@patch("requests.get")
def test_retrieve_fish_data_parses_excel_file(mocked_get):
    with open("tests/data/Daily_POSWFM_27_February_2023.xls", "rb") as f:
        mocked_get.return_value = Mock(status_code=201, content=f.read())

    from fetch_fish import retrieve_fish_data

    records = retrieve_fish_data(
        daily_fish_url="http://random_url",
        market="My market",
        year=2023,
        month="February",
        day="27",
    )
    assert len(records) > 0

    # check the date that is specified matches what is passed as a record
    expected_date = datetime.datetime(int(2023), int(2), int(27))
    assert records[0]["date"] == expected_date

    # check that we retrieve records correctly from the file
    assert len(records) == 50

    # Ensure expected fields in the record
    expected_fields = [
        "commodity",
        "unit",
        "volume",
        "average_price",
        "frequent_price",
        "min_price",
        "max_price",
    ]
    record = records[0]
    for field in expected_fields:
        assert field in record

    # check that the King Fish record makes sense
    for record in records:
        assert isinstance(record["commodity"], str)
        assert isinstance(record["unit"], str)

        if record["commodity"].lower() == "king fish":
            assert record["unit"].lower() == "kg"
