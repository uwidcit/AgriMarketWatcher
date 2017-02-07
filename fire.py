from firebase import firebase	
from firebase_token import firebase
import fetcher
from pymongo import MongoClient
import pymongo
import datetime
import copy
from parse_rest.installation import Push
from parse_rest.connection import register



Firebase =firebase.FirebaseApplication('https://agriprice-6638d.firebaseio.com/')
push_service = FCMNotification(api_key="AAAAJkFqwS4:APA91bHWbSUhyDuBx2XUC4o1hmzYA3gVgF3lCaj72F0LEnzBxa6Q5NlLLzCk-QXVojFnOV8HxY6_41jtV2GDRXEH51SXgQyI56gpIvZexjiKQtUUJ6Nh0648H4j8asxmiUsYBpwi7-0Ccd_pluLa0N9ebAd-EzLxcA")

def sendFire(recsCurrent):
	 
		crops =recsCurrent
		market = ["NWM","OVFM","POS"]
		dates = crops[0]['date'].ctime().split( )
		year = dates[4]
		day = dates[2]
		month = dates[1]
		root = market[0] + "/" + year +"/"+ month +"/" + day + "/"
		for i in crops:
			i['commodity'] = i['commodity'].replace(".", "")
			cat = "Category/" +i['category'] + "/"
			com = "Commodity/"  
			Firebase.put(root + cat + com , i['commodity'],i)
	



if __name__ == '__main__':
	sendFire()
