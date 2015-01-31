from pymongo import MongoClient
import pymongo
import operator
import datetime
import copy
from sklearn import linear_model

def predict():
	clf = linear_model.LinearRegression()
	clf.predict([[10, 2010], [12, 2011], [11, 2012]]),
	print clf.coef_

predict()