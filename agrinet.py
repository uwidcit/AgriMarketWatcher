from flask import Flask, request, make_response, render_template, current_app
from flask_autodoc.autodoc import Autodoc

from pymongo import MongoClient
from bson import json_util, objectid
from datetime import datetime, timedelta
import re  # regular expression
import os
import fetcher

from functools import update_wrapper
from fisheries import fisheries_file

app = Flask(__name__)
app.register_blueprint(fisheries_file)  # Add the fisheries related functionality to file
auto = Autodoc(app)  # https://github.com/acoomans/flask-autodoc

# Detect If Running in Development mode or on server
if "ENV" in os.environ:
    app.debug = False
else:
    app.debug = True

# mongo = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
# mongo.db = mongo['heroku_app24455461']

from dataManager import mongo


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            h['Access-Control-Allow-Headers'] = \
                "Origin, X-Requested-With, Content-Type, Accept, Authorization"
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)

    return decorator


# Helper/Utility functions
def convert_compatible_json(crop):
    crop["date"] = crop["date"].strftime('%Y-%m-%dT%H:%M:%S')  # convert the date object to a string
    crop["id"] = str(crop["_id"])  # convert mongodb id to a string
    del crop["_id"]  # remove original key
    return crop


def process_results(cursor):
    res = []
    for c in cursor:  # Iterates through each result from the mongodb result cursor
        res.append(convert_compatible_json(c))  # Pushes (appends) result to a list of results
    return res


def format_crop_query(crop):
    return {"commodity": crop}


def format_category_query(category):
    qry = []
    category = category.upper().split(",")
    for c in category:
        qry.append({"category": re.compile(c, re.IGNORECASE)})

    res = {"$or": qry} if (len(qry) > 1) else qry[0]  # http://en.wikipedia.org/wiki/Conditional_operator#Python
    return res


def process_options(options, req):
    if len(req.args) > 0:
        # convert to case insensitive search for crop name
        if req.args.get("crop"):
            options['commodity'] = re.compile(str(req.args.get("crop")), re.IGNORECASE)
        if req.args.get("commodity"):
            options['commodity'] = re.compile(str(req.args.get("commodity")), re.IGNORECASE)
        if req.args.get("category"):
            options.update(format_category_query(req.args.get("category")))
        if req.args.get("date"):
            try:  # check if the date is either in one of the two supported formats
                options['date'] = datetime.strptime(str(req.args.get('date')), '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                options['date'] = datetime.strptime(str(req.args.get('date')), '%Y-%m-%d')

    if len(options) > 1:  # if more than one dimension added we perform an or operation as opposed to an and
        qry = []
        for key in options.keys():
            print(key)
            qry.append({key: options[key]})  # convert the dictionary to a list of dictionaries
        options = {"$or": qry}  # combine each dictionary in the list to a single dictionary combined with or operator

    return options


# Display Pages
@app.route("/")
@crossdomain(origin='*')
def home():
    links = []
    return render_template("main.html", links=links)


@app.route("/about")
def about():
    return render_template("about.html")


# Meta API
# Returns the list of crops available
@app.route('/crops')
@auto.doc()
@crossdomain(origin='*')
def crops_list():
    """Returns a List of all of the crops (commodities) within the database."""
    crops = mongo.db.daily.distinct("commodity")
    return json_util.dumps(crops)


@app.route('/crops/categories')  #
@auto.doc()
@crossdomain(origin='*')
def crop_categories():
    """Returns the list of categories to which crops can belong."""
    res = mongo.db.daily.distinct("category")
    return json_util.dumps(res)


@app.route('/crops/categories/<category>')
@auto.doc()
@crossdomain(origin='*')
def crops_by_category(category=None):
    """Returns the list of crops which belong to the specified category."""
    res = mongo.db.daily.find({"category": category.upper()}).distinct("commodity")
    return json_util.dumps(res)


# Daily API
@app.route('/crops/daily')  #
@auto.doc()
@crossdomain(origin='*')
def crops_all_daily():
    """Returns the daily prices of all the crops."""
    options = {}
    offset = 0
    limit = 100
    if len(request.args) > 0:
        if request.args.get("limit"):  # Check limit to determine how much records to return
            limit = int(request.args.get("limit"))
        if request.args.get("offset"):  # Check offset to determine which record to start from
            offset = int(request.args.get("offset"))

    options = process_options(options, request)
    crops = mongo.db.daily.find(options).sort([("date", -1)]).skip(offset).limit(limit)
    res = process_results(crops)
    return json_util.dumps(res, default=json_util.default)


@app.route('/crops/daily/<cid>')
@auto.doc()
@crossdomain(origin='*')
def crops_id(cid=None):
    """Returns the daily price for a specific crop identified by its ID."""
    crops = mongo.db.daily.find({"_id": objectid.ObjectId(cid)})
    res = process_results(crops)
    return json_util.dumps(res, default=json_util.default)


@app.route("/crops/daily/dates")  # returns all the daily dates available
@app.route("/crops/daily/dates/<date>")  # returns the commodities for the date specified
@auto.doc()
@crossdomain(origin='*')
def daily_dates_list(date=None):
    res = []
    options = {}
    offset = 0
    limit = 100
    try:
        if date:
            try:  # check if the date is either in one of the two supported formats
                options['date'] = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                options['date'] = datetime.strptime(date, '%Y-%m-%d')

            if len(request.args) > 0:
                if request.args.get("limit"):  # Check limit to determine how much records to return
                    limit = int(request.args.get("limit"))
                if request.args.get("offset"):  # Check offset to determine which record to start from
                    offset = int(request.args.get("offset"))

            options = process_options(options, request)
            crops = mongo.db.daily.find(options).sort("date", -1).skip(offset).limit(limit)
            res = process_results(crops)
        else:
            end = datetime.now()
            start = end - timedelta(days=300)  # default to 30 days difference
            options = {"date": {'$gte': start, '$lt': end}}  # between dates syntax for mongodb
            dates = mongo.db.daily.find(options).distinct("date")
            res = map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'), dates)
            return json_util.dumps(res)

    except Exception as e:
        print(e)

    return json_util.dumps(res)


@app.route('/crops/daily/recent')  # Returns the daily prices of the most recent entry
@app.route('/crops/daily/recent/<crop>')  # Returns the most recent daily price of the specified comodity
@auto.doc()
@crossdomain(origin='*')
def most_recent_daily_data(crop=None):
    if crop:
        crops = mongo.db.dailyRecent.find(format_crop_query(crop))  # If we have a crop that we want to obtain
    else:
        crops = mongo.db.dailyRecent.find()  # Else, if we want all crops
    result = process_results(crops)
    return json_util.dumps(result, default=json_util.default)


@app.route('/crops/daily/category')
@app.route('/crops/daily/category/<category>')
@auto.doc()
@crossdomain(origin='*')
def crop_daily_categories(category=None):
    offset = 0
    limit = 100

    if len(request.args) > 0:
        if request.args.get("limit"):  # Check limit to determine how much records to return
            limit = int(request.args.get("limit"))
        if request.args.get("offset"):  # Check offset to determine which record to start from
            offset = int(request.args.get("offset"))

    if category:
        options = process_options(format_category_query(category), request)
        crops = mongo.db.daily.find(options).sort("date", -1).skip(offset).limit(limit)
        res = process_results(crops)
    else:
        res = mongo.db.daily.distinct("category")

    return json_util.dumps(res, default=json_util.default)


@app.route('/crops/daily/commodity/<commodity>')
@auto.doc()
@crossdomain(origin='*')
def crop_daily_commodity(commodity=None):
    res = []
    if commodity:
        commodity = commodity.lower().split(",")
        qry = []
        for c in commodity:
            qry.append({"commodity": c})
        crops = mongo.db.daily.find({"$or": qry})
        res = process_results(crops)

    return json_util.dumps(res, default=json_util.default)


@app.route('/crops/daily/predict')  # Returns the daily prices of the most recent entry
@app.route('/crops/daily/predict/<crop>')  # Returns the most recent daily price of the specified comodity
@auto.doc()
@crossdomain(origin='*')
def prediction_data(crop=None):
    if crop:
        crops = mongo.db.predictions.find({"name": crop})  # If we have a crop that we want to obtain
    else:
        crops = mongo.db.predictions.find()  # Else, if we want all crops
    result = crops
    return json_util.dumps(result, default=json_util.default)


# Monthly API

@app.route("/crops/monthly/dates")
@auto.doc()
@crossdomain(origin='*')
def monthly_dates_list():
    end = datetime.now()
    start = end - timedelta(days=300)  # default to 30 days difference
    query = {"date": {'$gte': start, '$lt': end}}  # between dates syntax for mongodb
    dates = mongo.db.monthly.find(query).distinct("date")
    dates = map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'), dates)
    return json_util.dumps(dates)


@app.route('/crops/monthly')
@app.route('/crops/monthly/<date>')
@auto.doc()
@crossdomain(origin='*')
def monthly_crops(date=None):
    res = []
    options = {}
    offset = 0
    limit = 100
    try:
        if date:
            if date != "all":  # if the date is all then no specified date query will return all
                try:  # check if the date is either in one of the two supported formats
                    options['date'] = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                except ValueError:
                    options['date'] = datetime.strptime(date, '%Y-%m-%d')
        else:
            d = datetime.now()
            d = d - timedelta(days=150)
            options['date'] = {'$gte': d, '$lt': datetime.now()}

        if len(request.args) > 0:
            if request.args.get("limit"):  # Check limit to determine how much records to return
                limit = int(request.args.get("limit"))
            if request.args.get("offset"):  # Check offset to determine which record to start from
                offset = int(request.args.get("offset"))

        options = process_options(options, request)
        crops = mongo.db.monthly.find(options).sort("date", -1).skip(offset).limit(limit)
        res = process_results(crops)
    except Exception, e:
        print e

    return json_util.dumps(res, default=json_util.default)


@app.route('/crops/monthly/category/')
@app.route('/crops/monthly/category/<category>')
@auto.doc()
@crossdomain(origin='*')
def monthly_crop_category(category=None):
    res = []
    options = {}
    offset = 0
    limit = 100

    try:
        if category:
            if len(request.args) > 0:
                if request.args.get("limit"):  # Check limit to determine how much records to return
                    limit = int(request.args.get("limit"))
                if request.args.get("offset"):  # Check offset to determine which record to start from
                    offset = int(request.args.get("offset"))

            options = process_options(options, request)
            options.update(format_category_query(category))  # merge the two dictionaries together

            crops = mongo.db.daily.find(options).sort("date", -1).skip(offset).limit(limit)
            res = process_results(crops)
        else:
            res = mongo.db.monthly.distinct("category")
    except Exception, e:
        print e

    return json_util.dumps(res, default=json_util.default)


@app.route('/crops/monthly/commodity/')
@app.route('/crops/monthly/commodity/<commodity>')
@auto.doc()
@crossdomain(origin='*')
def monthly_crop_commodity(commodity=None):
    res = []
    options = {}
    offset = 0
    limit = 10
    qry = []

    try:
        if commodity:
            if len(request.args) > 0:
                if request.args.get("limit"):  # Check limit to determine how much records to return
                    limit = int(request.args.get("limit"))
                if request.args.get("offset"):  # Check offset to determine which record to start from
                    offset = int(request.args.get("offset"))

            options = process_options(options, request)

            commodity = commodity.lower().split(",")
            for c in commodity:
                qry.append({"commodity": c})

            options = options.update({"$or": qry})

            crops = mongo.db.daily.find(options).sort("date", -1).skip(offset).limit(limit)
            res = process_results(crops)
        else:
            res = mongo.db.monthly.distinct("commodity")
    except Exception, e:
        print e

    return json_util.dumps(res, default=json_util.default)


@app.route('/documentation')
def documentation():
    return auto.html()


@app.route('/api/test/fetch')
def test_fetcher():
    recs_current = fetcher.getMostRecent()
    return json_util.dumps(recs_current, default=json_util.default)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
