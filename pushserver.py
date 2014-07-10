import fetcher
from pymongo import MongoClient
import pymongo
from pusher import Pusher
import operator

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


def handleDailyDifference(before, current):
	if before[0]['date'] != current[0]['date']:
		p = createPushConnection()
		# before.sort(key=operator.itemgetter('commodity'))
		# current.sort(key=operator.itemgetter('commodity'))
		for b in before:
			for c in current:
				if b['commodity'] == c['commodity']:
					if b['price'] != c['price']:
						print "found mis match in price"
						p['daily'].trigger(c['commodity'], {'message': { 'commodity': c['commodity'], 'date': c['date'].strftime('%Y-%m-%dT%H:%M:%S'), 'price': c['price'], 'previous': b['price'] }})
					break


def handleMonthlyDifference(before, current):
	if before[0]['date'] != current[0]['date']:
		p = createPushConnection()
		# before.sort(key=operator.itemgetter('commodity'))
		# current.sort(key=operator.itemgetter('commodity'))

		for b in before:
			for c in current:
				if b['commodity'] == c['commodity']:
					if b['mean'] != c['mean']:
						print "found mis match in price"
						p['monthly'].trigger(c['commodity'], {'message': { 'commodity': c['commodity'], 'date': c['date'].strftime('%Y-%m-%dT%H:%M:%S'), 'mean': c['mean'], 'previous': b['mean'] }})
					break

def run():
	db = connect2DB()
	if db:
		recsCurrent = fetcher.getMostRecent()
		print recsCurrent['daily'][0]
		print recsCurrent['monthly'][0]

		if recsCurrent:
			handleMonthlyDifference(list(db.recentMonthly.find()), recsCurrent['monthly'])
			handleDailyDifference(list(db.dailyRecent.find()), recsCurrent['daily'])

# run()

def conversionTesting():
	db = connect2DB()
	if db:
		recsD = list(db.dailyRecent.find())
		recsD.sort(key=operator.itemgetter('commodity'))

		recsD2 = map(lambda x: x['date'])

		handleDailyDifference

	

conversionTesting();
