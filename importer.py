import os
from pymongo import MongoClient

def list_files(directory):

	file_list = []
	for file in os.listdir(directory):
		dirfile = os.path.join(directory, file)
		if os.path.isfile(dirfile):
			print file
			file_list.append(dirfile)

list_files("./xls")

# def testPyMongo():
# 	# client = MongoClient(host='mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057' )
# 	mongo = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
# 	mongo.db = mongo['heroku_app24455461']
# 	print mongo.db
# 	# client = MongoClient('ds043057.mongolab.com', 43057)
# 	# client.heroku_app24455461.authenticate('agriapp', 'simplePassword')
# 	print mongo.db.daily.distinct("commodity")

# testPyMongo()