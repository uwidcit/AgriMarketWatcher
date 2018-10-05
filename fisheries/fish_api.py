from flask import Blueprint, current_app, request, make_response
from dataManager import mongo
from bson import json_util
from datetime import datetime, timedelta
from functools import update_wrapper

fisheries_file = Blueprint('fisheries_file', __name__)


def convert_compatible_json(fish):
    fish["date"] = fish["date"].strftime('%Y-%m-%dT%H:%M:%S')  # convert the date object to a string
    fish["id"] = str(fish["_id"])  # convert mongodb id to a string
    del fish["_id"]  # remove original key
    return fish


def process_results(cursor):
    res = []
    for c in cursor:  # Iterates through each result from the mongodb result cursor
        res.append(convert_compatible_json(c))  # Pushes (appends) result to a list of results
    return res


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


@fisheries_file.route("/fishes")
@crossdomain(origin='*')
def fish_list():
    fishes = mongo.db.dailyFishRecent.distinct('commodity')
    return json_util.dumps(fishes, indent=4)


@fisheries_file.route('/fishes/daily/recent')  # Returns the daily prices of the most recent entry
@fisheries_file.route('/fishes/daily/recent/<fish>')  # Returns the most recent daily price of the specified comodity
@crossdomain(origin='*')
def most_recent_daily_fish(fish=None):
    if fish:
        fishes = mongo.db.dailyFishRecent.find({"commodity": fish})  # If we have a crop that we want to obtain
    else:
        fishes = mongo.db.dailyFishRecent.find()  # Else, if we want all crops
    result = process_results(fishes)
    return json_util.dumps(result, default=json_util.default, indent=4)


@fisheries_file.route('/fishes/markets')
def market_list():
    markets = [{
        'name': 'Port of Spain Fish Market',
        'code': 'POSWFM'
    }, {
        'name': 'Orange Valley Fish Market',
        'code': 'OVWFM'
     }]
    return json_util.dumps(markets, indent=4)


@fisheries_file.route('/fishes/daily/recent/market/<market>')
def most_recent_daily_fish_by_market(market):
    fishes = mongo.db.dailyFishRecent.find({"market": market})
    result = process_results(fishes)
    return json_util.dumps(result, default=json_util.default, indent=4)


if __name__ == "__main__":  # executed by running python -m fisheries.fish_api from project root
    print("Running the API calls for simple validation")
    # print(fish_list())
    print(market_list())
    # print(most_recent_daily_fish())
    # print(most_recent_daily_fish('pampano'))
    print(most_recent_daily_fish_by_market("POSWFM"))
