from firebase import firebase	
import fetcher
from pymongo import MongoClient
import pymongo
import datetime
import copy
from parse_rest.installation import Push
from parse_rest.connection import register

Firebase =firebase.FirebaseApplication('https://agriprice-6638d.firebaseio.com/')


def connect2DB():
	try:
		client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
		db = client.get_default_database()
		return db
	except Exception as e:
		print e.strerror
		return None

# Firebase.put(root,{'Category':stuff[2]['category']} )


def sendFire():
	db = connect2DB()
	if db:
		recsCurrent = fetcher.getMostRecent()
		stuff =recsCurrent['daily']
		dates = stuff[0]['date'].ctime().split( )
		year = dates[4]
		day = dates[2]
		month = dates[1]
		root = year +"/"+ month +"/" + day + "/"
		for i in stuff:
			i['commodity'] = i['commodity'].replace(".", "")
			cat = "Category/" +i['category'] + "/"
			com = "Commodity/" +i['commodity'] + "/"
				# price = "Price" + 
			Firebase.put(root + cat + com , "Price",i['price'])
			Firebase.put(root + cat + com ,"Unit",i['unit'])



# def sendFire():
	
# 		year = 2017
# 		day = 1
# 		month = dates[1]
# 		root = year +"/"+ month +"/" + day + "/"
# 		for i in stuff:
# 			cat = "Category/" +i['category'] + "/"
# 			com = "Commodity/" +i['commodity'] + "/"
# 			# price = "Price" + 
# 			Firebase.put(root + cat + com , "Price",i['price'])
# 		# 	Firebase.put(root + cat + com + "/Price",i['price'],"/Volume",i['volume'])

if __name__ == '__main__':
	sendFire()
