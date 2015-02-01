from pymongo import MongoClient
import pymongo
import operator
import datetime
import copy
from sklearn import linear_model

MAX_DIFF = 0.5

def predict():
	clf = linear_model.LinearRegression()
	clf.predict([[10, 2010], [12, 2011], [11, 2012]]),
	print clf.coef_

def evalPrediction(expected, actual):
    if abs(expected - actual) == MAX_DIFF:
        return False
    return True

def storePredictions(db, dData):
	length = 0
	if (dData and len(dData) > 0):
		db.drop_collection("predictions")
		predictions = db.predictions
		predictions.insert(dData)
		length = predictions.count()
	return length