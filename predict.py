from pymongo import MongoClient
import pymongo
import operator
import datetime
import copy
from sklearn import linear_model

MAX_DIFF = 0.5

def predict():
	clf = linear_model.LinearRegression()
	Y_arr = [4.7, 6.5, 5.5, 7.5]
	X_arr = [[2011, 1], [2012, 2], [2013, 3], [2014, 4]]
	clf.fit(X_arr, Y_arr)
	coef = clf.coef_
	#print coef
	#print coef[1]*2 + coef[0]
	ans = clf.predict([2015, 5])
	print ans

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

predict()