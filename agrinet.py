import os
from datetime import datetime

from flask import Flask, render_template
from flask_json import FlaskJSON, as_json
from flask_redis import FlaskRedis

from app_util import crossdomain
from log_configuration import logger


def initialize_flask():
    # Define the Flask App
    flask_app = Flask(__name__)
    # Setup the Flask JSON Plugin
    FlaskJSON(flask_app)
    # Detect If Running in Development mode or on server
    flask_app.debug = False if "ENV" in os.environ else True
    # Retrieve data from the environment and add it to Flask App environment
    redis_conn_uri = os.getenv("REDISCLOUD_URL")
    if redis_conn_uri:
        flask_app.config["REDIS_URL"] = redis_conn_uri

    if flask_app.testing:
        from mockredis import MockRedis

        redis_client = FlaskRedis.from_custom_provider(MockRedis)
    else:
        # Setup the Flask Redis Plugin
        redis_client = FlaskRedis(flask_app)

    return flask_app, redis_client


app, redis_client = initialize_flask()


def process_query(target_class, query, req):
    if len(req.args) > 0:
        # convert to case insensitive search for crop name
        if req.args.get("crop"):
            query_by_crop = str(req.args.get("crop"))
            print(query_by_crop)
        elif req.args.get("commodity"):
            query_by_commodity = str(req.args.get("commodity"))
            print(query_by_commodity)
        elif req.args.get("category"):
            query_by_category = str(req.args.get("category"))
            print(query_by_category)
        elif req.args.get("date"):
            try:  # check if the date is either in one of the two supported formats
                query_by_date = datetime.strptime(
                    str(req.args.get("date")), "%Y-%m-%dT%H:%M:%S"
                )
            except ValueError:
                query_by_date = datetime.strptime(str(req.args.get("date")), "%Y-%m-%d")
            print(query_by_date)

    return query


@app.route("/api/admin/crops")
@as_json
def clean_up_and_fetch_crops():
    from models import delete_crop_records
    from pushserver import run

    delete_crop_records()

    return run(notify=False, override=True)


# Display Pages
@app.route("/")
@crossdomain(origin="*")
def home():
    links = []
    return render_template("main.html", links=links)


@app.route("/about")
def about():
    return render_template("about.html")


# Meta API
# Returns the list of crops available
@app.route("/crops")
@crossdomain(origin="*")
@as_json
def crops_list():
    """Returns a List of all of the crops (commodities) within the database."""
    from models import get_distinct_commodity

    return get_distinct_commodity()


@app.route("/crops/categories")  #
@crossdomain(origin="*")
@as_json
def crop_categories():
    """Returns the list of categories to which crops can belong."""
    from models import get_distinct_categories

    return get_distinct_categories()


@app.route("/crops/categories/<category>")
@crossdomain(origin="*")
@as_json
def crops_by_category(category=None):
    """Returns the list of crops which belong to the specified category."""
    from models import get_distinct_commodity_by_category

    return get_distinct_commodity_by_category(category)


# Daily Crop API
@app.route("/crops/daily")  #
@crossdomain(origin="*")
@as_json
def crops_all_daily():
    """Returns the daily prices of all the crops."""
    from models import get_daily

    try:
        daily_crops = get_daily()
        if not daily_crops:
            daily_crops = fetch_latest()["crops"]
        return daily_crops
    except Exception:
        return None, 500


@app.route("/crops/daily/<cid>")
@crossdomain(origin="*")
@as_json
def crops_id(cid=None):
    """Returns the daily price for a specific crop identified by its ID."""
    from models import get_daily_by_id

    try:
        return get_daily_by_id(int(cid))
    except Exception:
        return None, 404


@app.route("/crops/daily/dates")  # returns all the daily dates available
@crossdomain(origin="*")
@as_json
def daily_dates_list():
    """returns all the daily dates available or returns the commodities for the date specified"""
    from models import get_daily_dates

    dates = get_daily_dates()
    return dates or []


@app.route("/crops/daily/dates/<request_date>")  # returns all the daily dates available
@crossdomain(origin="*")
@as_json
def get_daily_crops_by_date(request_date=None):
    """returns all the daily dates available or returns the commodities for the date specified"""
    app.logger.warning(
        f"No longer support more than the current date. The date {request_date} will be ignored"
    )
    return crops_all_daily()


@app.route("/crops/daily/recent")  # Returns the daily prices of the most recent entry
# Returns the most recent daily price of the specified commodity
@app.route("/crops/daily/recent/<crop>")
@crossdomain(origin="*")
@as_json
def most_recent_daily_data(crop=None):
    """Returns the daily prices of the most recent entry
    or the most recent daily price of the specified commodity."""
    from models import get_most_recent_daily

    if crop:  # If we have a crop that we want to obtain
        try:
            return crop_daily_commodity(crop)
        except Exception:
            return None, 404
    else:
        try:
            daily_crops = get_most_recent_daily()
            if not daily_crops:
                logger.info("Unable to retrieve records. Retrieving records")
                daily_crops = fetch_latest()["crops"]
            return daily_crops
        except Exception:
            return None, 500


@app.route("/crops/daily/category")  # list categories available to daily crops
@app.route("/crops/daily/category/<category>")  # get daily crops  by categories
@crossdomain(origin="*")
@as_json
def crop_daily_categories(category=None):
    from models import get_distinct_categories, get_distinct_commodity_by_category

    if category:
        try:
            return get_distinct_commodity_by_category(category)
        except Exception:
            return None, 404
    else:
        return get_distinct_categories()


@app.route("/crops/daily/commodity/<commodity>")
@crossdomain(origin="*")
@as_json
def crop_daily_commodity(commodity=None):
    from models import get_daily_recent_by_commodity

    try:
        crops = get_daily_recent_by_commodity(commodity)
        if crops:
            return crops
        else:
            return None, 404
    except Exception:
        return None, 404


@app.route("/latest")
@crossdomain(origin="*")
@as_json
def fetch_latest():
    from pushserver import run

    return run(notify=False)


# ***** Fish-related endpoints


@app.route("/fishes")
@crossdomain(origin="*")
@as_json
def fish_list():
    from models import get_distinct_fish_commodity

    return get_distinct_fish_commodity()


@app.route("/fishes/daily/recent")
@app.route("/fishes/daily/recent/<fish>")
@crossdomain(origin="*")
@as_json
def most_recent_daily_fish_merged(fish=None):
    """
    if fish specified, returns the most recent daily price of the specified comodity
    else Returns the daily prices of the most recent entry
    """
    from models import get_daily_recent_by_commodity_fish, get_most_recent_daily_fish

    if fish:  # If we have a crop that we want to obtain
        fishes = get_daily_recent_by_commodity_fish(fish)
        if not fishes:
            return None, 404
    else:
        fishes = get_most_recent_daily_fish()
    return fishes


@app.route("/fishes/markets")
@crossdomain(origin="*")
@as_json
def market_list():
    return [
        {"name": "Port of Spain Fish Market", "code": "POSWFM"},
        {"name": "Orange Valley Fish Market", "code": "OVWFM"},
    ]


@app.route("/fishes/daily/recent/market/<market>")
@crossdomain(origin="*")
@as_json
def most_recent_daily_fish_by_market(market):
    return []


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, threaded=True)
