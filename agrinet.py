import os
from datetime import datetime
from log_configuration import logger

from flask import Flask, request, render_template
from flask_json import FlaskJSON, as_json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, desc, asc

from app_util import crossdomain, process_results
from fisheries import fisheries_file

app = Flask(__name__)
FlaskJSON(app)

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///agrimarketwatcher.db")
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

app.register_blueprint(
    fisheries_file
)  # Add the fisheries related functionality to file
# Detect If Running in Development mode or on server
app.debug = False if "ENV" in os.environ else True


def process_query(target_class, query, req):
    if len(req.args) > 0:
        # convert to case insensitive search for crop name
        if req.args.get("crop"):
            query = query.filter(
                func.lower(target_class.commodity)
                == func.lower(str(req.args.get("crop")))
            )
        elif req.args.get("commodity"):
            query = query.filter(
                func.lower(target_class.commodity)
                == func.lower(str(req.args.get("commodity")))
            )
        elif req.args.get("category"):
            query = query.filter(
                func.lower(target_class.category)
                == func.lower(str(req.args.get("category")))
            )
        elif req.args.get("date"):
            try:  # check if the date is either in one of the two supported formats
                query_date = datetime.strptime(
                    str(req.args.get("date")), "%Y-%m-%dT%H:%M:%S"
                )
            except ValueError:
                query_date = datetime.strptime(str(req.args.get("date")), "%Y-%m-%d")
            query = query.filter(func.DATE(target_class.date) == query_date)
    return query


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

    return get_distinct_commodity_by_category(category.upper())


# Daily API
@app.route("/crops/daily")  #
@crossdomain(origin="*")
@as_json
def crops_all_daily():
    """Returns the daily prices of all the crops."""
    from models import DailyCrops

    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0

    query = db.session.query(DailyCrops)
    query = process_query(DailyCrops, query, request)

    query_results = query.limit(limit).offset(offset).all()
    return process_results(query_results)


@app.route("/crops/daily/<cid>")
@crossdomain(origin="*")
@as_json
def crops_id(cid=None):
    """Returns the daily price for a specific crop identified by its ID."""
    if cid is not None and cid.isdigit():
        from models import get_daily_by_id

        return get_daily_by_id(cid).as_dict()
    else:
        return None, 404


@app.route("/crops/daily/dates")  # returns all the daily dates available
@app.route(
    "/crops/daily/dates/<date>"
)  # returns the commodities for the date specified
@crossdomain(origin="*")
@as_json
def daily_dates_list(date=None):
    """returns all the daily dates available or returns the commodities for the date specified"""
    from models import DailyCrops

    res = []

    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0

    try:
        if date:
            query = db.session.query(DailyCrops)

            try:  # check if the date is either in one of the two supported formats
                query_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                try:
                    query_date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    logger.error(
                        "Received an invalid date from the user {0}".format(date)
                    )
                    return [], 404

            query = query.filter(func.DATE(DailyCrops.date) == query_date)
            query = process_query(DailyCrops, query, request)

            query_results = query.limit(limit).offset(offset).all()
            return process_results(query_results)
        else:
            records = (
                db.session.query(DailyCrops.date)
                .distinct()
                .order_by(asc(DailyCrops.date))
                .limit(limit)
                .offset(offset)
                .all()
            )
            res = [rec.date.strftime("%Y-%m-%dT%H:%M:%S") for rec in records]
    except Exception as e:
        logger.error(e)

    return res


@app.route("/crops/daily/recent")  # Returns the daily prices of the most recent entry
@app.route(
    "/crops/daily/recent/<crop>"
)  # Returns the most recent daily price of the specified commodity
@crossdomain(origin="*")
@as_json
def most_recent_daily_data(crop=None):
    """Returns the daily prices of the most recent entry or the most recent daily price of the specified commodity."""
    from models import get_most_recent_daily, get_daily_recent_by_commodity

    if crop:  # If we have a crop that we want to obtain
        res = get_daily_recent_by_commodity(crop)  # TODO - fails unique constraint
        if not res:
            return None, 404
        crops = [res]
    else:
        crops = get_most_recent_daily()
    return process_results(crops)


@app.route("/crops/daily/category")  # list categories available to daily crops
@app.route("/crops/daily/category/<category>")  # get daily crops  by categories
@crossdomain(origin="*")
@as_json
def crop_daily_categories(category=None):
    from models import get_distinct_categories, DailyCrops

    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0

    if category:
        query = db.session.query(DailyCrops)
        query = query.filter(func.upper(DailyCrops.category) == func.upper(category))
        query = process_query(DailyCrops, query, request)
        query_results = query.limit(limit).offset(offset).all()
        res = process_results(query_results)
    else:
        res = get_distinct_categories()
    return res


@app.route("/crops/daily/commodity/<commodity>")
@crossdomain(origin="*")
@as_json
def crop_daily_commodity(commodity=None):
    from sqlalchemy import or_
    from models import DailyCropsRecent

    if commodity is not None and len(commodity) > 1:
        commodities = commodity.lower().split(",")
        query = db.session.query(DailyCropsRecent)
        query_results = query.filter(
            or_(DailyCropsRecent.commodity == v for v in commodities)
        ).all()
        return process_results(query_results)
    else:
        return [], 404


# Monthly API


@app.route("/crops/monthly/dates")
@crossdomain(origin="*")
@as_json
def monthly_dates_list():
    from models import MonthlyCrops

    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0
    records = (
        db.session.query(MonthlyCrops.date)
        .distinct()
        .order_by(desc(MonthlyCrops.date))
        .limit(limit)
        .offset(offset)
        .all()
    )
    return [rec.date.strftime("%Y-%m-%dT%H:%M:%S") for rec in records]


@app.route("/crops/monthly")
@app.route("/crops/monthly/<date>")
@crossdomain(origin="*")
@as_json
def monthly_crops(date=None):
    from models import MonthlyCrops

    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0
    try:
        query = db.session.query(MonthlyCrops)
        if date:
            try:  # check if the date is either in one of the two supported formats
                query_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                try:
                    query_date = datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    logger.error(
                        "Received an invalid date from the user {0}".format(date)
                    )
                    return [], 404

            query = query.filter(func.DATE(MonthlyCrops.date) == query_date)
            query = process_query(MonthlyCrops, query, request)
            query_results = query.limit(limit).offset(offset).all()
            return process_results(query_results)
        else:
            query = process_query(MonthlyCrops, query, request)
            query_results = query.limit(limit).offset(offset).all()
            return process_results(query_results)
    except Exception as e:
        logger.error(e)

    return []


@app.route("/crops/monthly/category/")
@app.route("/crops/monthly/category/<category>")
@crossdomain(origin="*")
@as_json
def monthly_crop_category(category=None):
    from models import get_distinct_categories, MonthlyCrops

    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0

    if category:
        query = db.session.query(MonthlyCrops)
        query = query.filter(func.upper(MonthlyCrops.category) == func.upper(category))
        query = process_query(MonthlyCrops, query, request)
        query_results = query.limit(limit).offset(offset).all()
        res = process_results(query_results)
    else:
        res = get_distinct_categories()
    return res


@app.route("/crops/monthly/commodity/")
@app.route("/crops/monthly/commodity/<commodity>")
@crossdomain(origin="*")
@as_json
def monthly_crop_commodity(commodity=None):
    limit = int(request.args.get("limit")) if request.args.get("limit") else 100
    offset = int(request.args.get("offset")) if request.args.get("offset") else 0

    try:
        from sqlalchemy import or_
        from models import MonthlyCrops

        if commodity is not None and len(commodity) > 1:
            commodities = commodity.lower().split(",")
            query = db.session.query(MonthlyCrops)
            query_results = (
                query.filter(or_(MonthlyCrops.commodity == v for v in commodities))
                .limit(limit)
                .offset(offset)
                .all()
            )
            return process_results(query_results)
        else:
            return [], 404
    except Exception as e:
        logger.error(e)

    return [], 500


@app.route("/latest")
@crossdomain(origin="*")
@as_json
def fetch_latest():
    from pushserver import run

    return run()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
