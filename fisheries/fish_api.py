from datetime import timedelta
from functools import update_wrapper

from flask import Blueprint, current_app, request, make_response
from flask import jsonify

from dataManager import mongo
from app_util import crossdomain

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


@fisheries_file.route("/fishes")
@crossdomain(origin='*')
def fish_list():
    fishes = mongo.db.dailyFishRecent.distinct('commodity')
    return jsonify(fishes)


@fisheries_file.route('/fishes/daily/recent')  # Returns the daily prices of the most recent entry
@fisheries_file.route('/fishes/daily/recent/<fish>')  # Returns the most recent daily price of the specified comodity
@crossdomain(origin='*')
def most_recent_daily_fish_merged(fish=None):
    if fish:
        fishes = mongo.db.dailyFishRecent.find({"commodity": fish})  # If we have a crop that we want to obtain
    else:
        fishes = mongo.db.dailyFishRecent.find()
    results = process_results(fishes)
    fishesRecs = {}
    for rec in results:
        commodity = rec['commodity']
        if commodity not in fishesRecs:
            fishesRecs[commodity] = {}
        fishesRecs[commodity][rec['market']] = rec
    # return json_util.dumps(fishesRecs, default=json_util.default, indent=4)
    return jsonify(fishesRecs)


@fisheries_file.route('/fishes/markets')
@crossdomain(origin='*')
def market_list():
    markets = [{
        'name': 'Port of Spain Fish Market',
        'code': 'POSWFM'
    }, {
        'name': 'Orange Valley Fish Market',
        'code': 'OVWFM'
    }]
    return jsonify(markets)


@fisheries_file.route('/fishes/daily/recent/market/<market>')
@crossdomain(origin='*')
def most_recent_daily_fish_by_market(market):
    fishes = mongo.db.dailyFishRecent.find({"market": market})
    result = process_results(fishes)
    # return json_util.dumps(result, default=json_util.default, indent=4)
    return jsonify(result)


if __name__ == "__main__":  # executed by running python -m fisheries.fish_api from project root
    print("Running the API calls for simple validation")
    # print(fish_list())
    # print(market_list())
    # print(most_recent_daily_fish())
    # print(most_recent_daily_fish('pampano'))
    # print(most_recent_daily_fish_by_market("POSWFM"))
    print(most_recent_daily_fish_merged())
