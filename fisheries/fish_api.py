from flask import Blueprint
from flask_json import as_json
from app_util import crossdomain, process_results

fisheries_file = Blueprint("fisheries_file", __name__)


@fisheries_file.route("/fishes")
@crossdomain(origin="*")
@as_json
def fish_list():
    from models import get_distinct_fish_commodity

    return get_distinct_fish_commodity()


@fisheries_file.route(
    "/fishes/daily/recent"
)  # Returns the daily prices of the most recent entry
@fisheries_file.route(
    "/fishes/daily/recent/<fish>"
)  # Returns the most recent daily price of the specified comodity
@crossdomain(origin="*")
@as_json
def most_recent_daily_fish_merged(fish=None):
    from models import get_most_recent_daily_fish, get_daily_recent_by_commodity_fish

    if fish:  # If we have a crop that we want to obtain
        res = get_daily_recent_by_commodity_fish(fish)  # TODO - fails unique constraint
        if not res:
            return None, 404
        fishes = [res]
    else:
        fishes = get_most_recent_daily_fish()
    return process_results(fishes)


@fisheries_file.route("/fishes/markets")
@crossdomain(origin="*")
@as_json
def market_list():
    return [
        {"name": "Port of Spain Fish Market", "code": "POSWFM"},
        {"name": "Orange Valley Fish Market", "code": "OVWFM"},
    ]


@fisheries_file.route("/fishes/daily/recent/market/<market>")
@crossdomain(origin="*")
@as_json
def most_recent_daily_fish_by_market(market):
    return []


# executed by running python -m fisheries.fish_api from project root
if __name__ == "__main__":
    print("Running the API calls for simple validation")
    # print(fish_list())
    # print(market_list())
    # print(most_recent_daily_fish())
    # print(most_recent_daily_fish('pampano'))
    # print(most_recent_daily_fish_by_market("POSWFM"))
    # print(most_recent_daily_fish_merged())
