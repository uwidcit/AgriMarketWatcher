from .dataManager import DatabaseManager, DataSource, NDNWMDaily
from pymongo import MongoClient

mongo = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
mongo.db = mongo['heroku_app24455461']

def connect2DB():
    return mongo.db