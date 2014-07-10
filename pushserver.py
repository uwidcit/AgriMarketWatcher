import fetcher
from pymongo import MongoClient
import pymongo
from pusher import Pusher
import operator
import datetime
import copy

def connect2DB():
	try:
		client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
		db = client.get_default_database()
		return db
	except Exception, e:
		print e
		return None

def createPushConnection():
	try:
		p = Pusher(app_id="81011", key="8749af531d18b551d367", secret="8bfde7e6e0293352ae71")
		return p
	except Exception, e:
		print e
		return None

def formatMessage(currrec,prevrec, type="daily"):
	message = {}

	if type == "daily":
		message = { 'commodity': currrec['commodity'], 'date': currrec['date'].strftime('%Y-%m-%dT%H:%M:%S'), 'price': currrec['price'], "previous": prevrec['price'] }
	else:
		message = { 'commodity': currrec['commodity'], 'date': currrec['date'].strftime('%Y-%m-%dT%H:%M:%S'), 'mean': currrec['mean'], "previous": prevrec['mean'] }

	return message

def updateGeneralDataSet(curr, prev, typeR="daily"):
	db = connect2DB()
	if db:
		if typeR == "daily":
			dateRec = db.daily.find().sort("date", -1).limit(1)
			if dateRec[0]['date'] != curr['date']:
				db.daily.insert(curr)
				print "from ", dateRec[0]['date'], " to", curr['date']
		else: #monthly
			dateRec = db.monthly.find().sort("date", -1).limit(1)
			if dateRec[0]['date'] != curr['date']:
				db.monthly.insert(curr)
				print "from ", dateRec[0]['date'], " to", curr['date']

def handleDifference(before, current, typeR="daily"):
	if before[0]['date'] != current[0]['date']:
		p = createPushConnection()
		if p:
			for b in before:
				for c in current:
					if b['commodity'] == c['commodity']:
						if b['price'] != c['price']:
							print "price for ", b['commodity'], " changed"
							# Add new record to the general dataset
							updateGeneralDataSet(c, b, typeR)
							# Send Push notification of change record
							event = c['commodity'].replace(" ", "").lower()
							message = formatMessage(c,b, typeR)
							p[typeR].trigger(event, {'message': message})
						else:
							print "price for ", b['commodity'], " remained the same"
						break
	else:
		print "no new record found"


def run():
	db = connect2DB()
	if db:
		recsCurrent = fetcher.getMostRecent()
		if recsCurrent:
			handleDifference(list(db.recentMonthly.find()), recsCurrent['monthly'], "monthly")
			handleDifference(list(db.dailyRecent.find()), recsCurrent['daily'], "daily")

run()

def dailyconverter(rec):
	rec['date'] = rec['date'] + datetime.timedelta(days=10)
	rec['price'] = rec['price'] + 1
	return rec

def conversionTesting():
	db = connect2DB()
	if db:
		recsD = list(db.dailyRecent.find())
		recs2 = copy.deepcopy(recsD)
		recs2 = list(map(dailyconverter, recs2))

		print len(recsD)
		print recsD[0]['price']
		print len(recs2)
		print recs2[0]['price']

		handleDailyDifference(recsD, recs2)

# conversionTesting();
