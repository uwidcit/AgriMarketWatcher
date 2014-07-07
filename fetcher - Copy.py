import urllib
import urllib2
import xlrd
from datetime import datetime
from xlrd import open_workbook
from pymongo import MongoClient
import pymongo
import json
import time
import datetime

category = "ROOT CROPS"
categories = ["root crops","condiments and spices","leafy vegetables","vegetables", "fruits","citrus"]


# Extracts the data from a row and returns a dictionary 
# @param sheet : the sheet to be processed
# @param row : the row number to be processed
# @param category : the category of the crop the be considered
# @return : a dictionary representing the data at the specified row 
#           for a particular sheet
def processDaily(sheet, row, category):
	dic = {}
	dic['commodity'] = sheet.cell_value(row, 0).encode('ascii').lower()
	dic['category'] = category.encode('ascii')
	dic['unit'] = sheet.cell_value(row, 1).encode('ascii')
	dic['volume'] = sheet.cell_value(row, 3)
	dic['price'] = sheet.cell_value(row, 6)

	if sheet.cell(row, 3) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or dic['volume'] == '':
		dic['volume'] = 0.0
	
	if sheet.cell(row, 6) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or dic['price'] == '':
		dic['price'] = 0.0
	
	return dic

def processMonthly(sheet, row, category):
	dic = {}
	dic['commodity'] = sheet.cell_value(row, 0).encode('ascii').lower()
	dic['category'] = category.encode('ascii')
	dic['unit'] = str(sheet.cell_value(row, 1)).encode('ascii')
	
	if sheet.cell(row, 2) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
		dic['min'] = 0.0
	else:
		dic['min'] = sheet.cell_value(row, 2)
	
	if sheet.cell(row, 3) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
		dic['max'] = 0.0
	else:	
		dic['max'] = sheet.cell_value(row, 3)
	
	if sheet.cell(row, 4) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
		dic['mode'] = 0.0
	else:	
		dic['mode'] = sheet.cell_value(row, 4)
	
	if sheet.cell(row, 5) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
		dic['mean'] = 0.0
	else:	
		dic['mean'] = sheet.cell_value(row, 5)
	
	if sheet.cell(row, 6) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
		dic['volume'] = 0.0
	else:	
		dic['volume'] = sheet.cell_value(row, 6)

	return dic

def processRow(sheet, row, type):
	global category
	global categories

	dic = {}

	#ensure that the row is not empty
	if sheet.cell_type(row, 0) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
		return None
	else:
		#Check if the second column is empty then usually for the category listing
		if not sheet.cell(row, 1).value:
			val = sheet.cell(row, 0).value
			#Check if in the valid list of categories
			if val.lower() in categories:
				category = val.upper()
		else:
			if type == "daily":
				return processDaily(sheet, row, category)
			else:
				return processMonthly(sheet, row, category)
		
def traverseWorkbook(url, params = {}, workbook_type = "daily"):
	values = []
	try:
		#print "Trying to read ", url
		data = urllib2.urlopen(url).read()
		print "Reading data ....."
		wb = open_workbook(url, file_contents=data)
		#print "Read workbook....."
		for s in wb.sheets():
			for row in range(s.nrows):
				if (workbook_type == "daily" and row > 10) or (workbook_type == "monthly" and row > 15) :
					#print "Processing row data"
					rowData = processRow(s, row, workbook_type)
					if rowData:
						values.append(rowData)
		return values;
	except Exception, e:
		print "Error in reading workbook at ", url
		print e
		return None

def retrieveFile(url, filename):
	try:
		req = urllib2.urlopen(url)
		CHUNK = 16 * 1024
		with open(filename, 'wb') as fp:
			while True:
				chunk = req.read(CHUNK)
				if not chunk: break
				fp.write(chunk)
		return True
	except Exception, e:
		return None

def get_url(base_url, year, month, day = None):
	months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	if (str(month).isdigit()):
		mStr = months[int(month) - 1]
	else:
		mStr = month
		months.index(month) + 1

	if day:
		return base_url +  "%20" + str(day) + "%20" + mStr + "%20" + str(year) + ".xls"
	else:
		url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Monthly/"+str(mStr)+"%20"+str(year)+"%20NWM%20Monthly%20Report.xls"
		return url



def retrieveDaily(base_url, day, month, year):
	filename = "daily" + "-" + str(day) + "-"+ str(month) + "-"+ str(year)+".xls"
	months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

	if (str(month).isdigit()):
		mStr = months[month - 1]
	else:
		mStr = month
		month = months.index(month) + 1


	url = base_url +  "%20" + str(day) + "%20" + mStr + "%20" + str(year) + ".xls";
	#url = urllib.unquote(url)

	#v = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-%2017%20June%202014.xls"
	#v = urllib.unquote(v)
	#print (url == v)
	#print url 
	#print v
	
	print "time: "+str(day)+"-"+str(mStr)+"-"+str(year)

	
	result = traverseWorkbook(url,workbook_type='daily')
	print "Got result"
	if result:
		#Add the date to each record
		for x in result:
			if x:
				print x
				x.update({'date':datetime.datetime(int(year),int(month),int(day))})	
				print "Updated successfully"		
			else:
				print "Removed"
				result.remove(x)	
		print "We have some resukt"		
		return result
	else:
		print "We have no result"
		return None

def retrieveMonthly(base_url,  month, year):
	filename = "monthly "+"-"+str(month)+"-"+str(year)+".xls"
	months = ["January","February","March","April","May","June","July","August","September","October","November","December"]

	if (str(month).isdigit()):
		mStr = months[month - 1]
	else:
		mStr = month
		month = months.index(month) + 1


	url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Monthly/"+str(mStr)+"%20"+str(year)+"%20NWM%20Monthly%20Report.xls"
	
	print "time: "+str(month)+"-"+str(year)

	# mInt = months.index(month) + 1
	result = traverseWorkbook(url, {}, "monthly")
	if result:
		for x in result:
			if x:
				x.update({"date": datetime.datetime(int(year), int(month), 1)})
		return result
	else:
		return None

def storeMonthly(db, mData):
	length = 0
	if (len(mData) > 0):
		monthly = db.monthly
		monthly.insert(mData)
		length = monthly.count()

	return length

def storeDaily(db, dData):
	length = 0
	if (dData and len(dData) > 0 ):
		daily = db.daily
		daily.insert(dData)
		length = daily.count()


	return length

def storeMostRecentDaily(db, dData):
	length = 0
	if (dData and len(dData) > 0):
		recent_daily = db.dailyRecent 
		recent_daily.insert(dData)
		length = recent_daily.count()
	return length

def storeMostRecentMonthly(db, dData):
	length = 0
	if (dbData and len(dbData) > 0):
		recent_monthly = db.recentMonthly 
		recent_monthly.insert(dData)
		length = recent_monthly.count()
	return length

# Ideas
# Create a document in the MongoDB database that stores the the most recent data in the database separately from
# the rest of the data in addition to loading the the data together with the current data
# we can then simply use the appropriate url to access the most recent data from the MongoDB
# 1.  

# To prevent the repeated parsing of xls files, we can store a list of read xls files


# Parses the json returned by mongoDB in the format for url logging and returns a set of urls
def extract_urls_from_json(j_obj):
	data = json.loads(j_obj)
	return data['url']


# Gets all of the sheets processed so far by the database
def get_processed_sheets(db):
	processed = db.processed.find()
	if not processed:
		return set()
	return set(map(lambda x : extract_urls_from_json(x), processed))


# Logs sheets that have just been processed into the database
def log_sheet_as_processed(db, sheet):
	db.processed.insert({'url' : sheet})

def getMostRecent():
	base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-"
	try:
		months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
			"October", "November", "December"]
		client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
		db = client.get_default_database()
		day = int(time.strftime("%d"))
		month_num = int(time.strftime("%m"))
		months_names = [months[month_num - 1]]
		months_names.append(months[11] if month_num == 1 else months[month_num - 2])
		year_number = int(time.strftime("%Y"))
		years = [year_number]
		reset_daily = False
		if month_num == 1:
			years.append(year_number - 1)
		d = None
		for year in years:
			for month in months_names:
				for day in reversed(range(day + 1)):
					url = get_url(base_url, str(year), str(month), str(day))
					#print "Checking URL: ", url
					d = retrieveDaily(base_url, str(day), month, str(year))
					#print "Tried to retrieve data"
					if d:
						reset_daily = True
						#print "Grabed data"
						break
					else:
						pass
						#print "No data for {0}/{1}/{2}".format(str(day), str(month), str(year))
				if reset_daily:
					break
			if reset_daily:
				break
		print "Found valid data"
			
		

		if reset_daily:
			db.drop_collection("dailyRecent")
			storeMostRecentDaily(db, d)





	except Exception, e:
		print e
	else:
		pass
	finally:
		print "Retieved most recent"


#getMostRecent()

def getAllDaily():

    # Here we attempt to retrieve the data from namistt
    daily = []
    most_recent_daily = None
    print "Attempting to retrieve all daily data"
    months = ["January", "February", "March", "April", "June", "July", "August", "September",
              "October", "November", "December"]
    base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-"
    for year in range(2012, 2015):
        for month in months:
            for day in range(1, 33):
                d = retrieveDaily(base_url, str(day), month, str(year))
                if d:
                    print d
                    daily.extend(d)
                    most_recent_daily = d
                else:
                    print "Data not found"

    # Now that we have collected all of the availible daily data, we will
    # attempt to log the data into the database

    print "Finished pulling data from namistt, begining to log the data"
    
    try:
        client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
        db = client.get_default_database()
        db.drop_collection("daily")
        num_stored = storeDaily(db, daily)
        storeMostRecentDaily(db, most_recent_daily)
        print str(num_stored) + " stored in database for daily records"
    except:
        print "Error in accessing database"


getAllDaily()

def runGetAll():
	print "Retrieving the all data"
	months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
	base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-"

	

	most_recent_daily = None
	most_recent_monthly = None
	daily = []
	monthly = []
	reset_daily = False
	reset_monthly = False


	
	#processed = get_processed_sheets(db)

	for year in range(2010, 2015):
		for month in months:
			m = retrieveMonthly(base_url, month, str(year))
			if m:
				monthly.extend(m)
				print "Logged for {0}-{1}".format(month, year)
				

	print "Finsheed processing months"


	for year in range(2010, 2015):
		for month in months:
			for day in range(1, 32):
				d = retrieveDaily(base_url, str(day), month, str(year))
				if d:
					#reset_daily = True
					daily.extend(d)
					print "Logged for {0}-{1}-{2}".format(day, month, year)
	print "Finished processing days"

	


	#for year in range(2007, 2015):
	#	for month in months:
	#		#extract daily reports
	#		for day in range(1,32):
	#			#url = get_url(base_url, str(year), str(month), str(day))
	#			if True:
	#				d = retrieveDaily(base_url, str(day), month, str(year))
	#				if d:
	#					#reset_daily = True
	#					daily.extend(d)
	#					#most_recent_daily = d
	#					#log_sheet_as_processed(db, url) # We are iterating through these properties in chronological order
    #                                      # Consequently, the last update the the most_recent will be the most recent data in the excel sheets  
	#		#extract monthly reports
	#		#url_month = get_url(base_url, month, str(year))
	#		if True:
	#			m = retrieveMonthly(base_url, month, str(year))
	#			if m:
	#				#reset_monthly = True
	#				monthly.extend(m)
					#most_recent_monthly = m 
					#log_sheet_as_processed(db, url_month)# Similar to the the most_recent_daily
	
	try:
		client =  MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")

		db = client.get_default_database()
		# db = client.agrinet			#removed this because it makes the application dependent on agrinet as database name

		#because we are pulling the entire collection we crop the records before reinserting
		db.drop_collection("daily")
		db.drop_collection("monthly")

		# If we have a new set of data for the daily information, we insert that into the database
		#if reset_daily:
		#	db.drop_collection("dailyRecent")
		#	storeMostRecentDaily(db, most_recent_daily)

		# If we have a new set of monthly data, we write that to the database
		#if reset_monthly:
		#	db.drop_collection("monthlyRecent")
		#	storeMostRecentMonthly(db, most_recent_monthly)
		
		print "Months " + str(len(monthly))
		print "Stored " + str(storeMonthly(db, monthly)) 

		print "Daily "  + str(len(daily))
		print "Stored " + str(storeDaily(db, daily))

		print "Retrieved and stored all files"
		

	except pymongo.errors.ConnectionFailure, e:
		print e	
	
#runGetAll() # run and extract the files from the server

def processDailyRec(rec, col):
	print rec

def testIndivid():
	daily_base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-"
	d = retrieveDaily(daily_base_url,19,"February",2014 )
	# print "daily " + str(len(d))
	# # print d[0]

	# m = retrieveMonthly("", "February", 2014)
	# print "monthly "+ str(len(m))
	# print m[0]

	# # print d 
	# print m[0]["date"].strftime("%Y-%B-%d")
	
	# client = MongoClient()
	# db = client.agrinet
	# daily = db.daily

	# if d:
	# 	print daily.insert(d)


	try:
		client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
		db = client.get_default_database()

		db.drop_collection("daily")
		# db.drop_collection("monthly")

		daily = db.daily
		# monthly  = db.monthly


		daily.insert(d)
		# monthly.insert(m)


		# print client.database_names()
		print daily.count()
		# print monthly.count()

	except pymongo.errors.ConnectionFailure, e:
		print e

# testIndivid()