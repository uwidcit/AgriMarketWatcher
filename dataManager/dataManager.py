# Reference URL: https://jeffknupp.com/blog/2014/06/18/improve-your-python-python-classes-and-object-oriented-programming/
import requests
import httplib2
import xlrd
from xlrd import open_workbook
import os
import json
from datetime import datetime
from pymongo import MongoClient
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))


# noinspection PyMethodMayBeStatic,PyBroadException
class DataSource(object):
	"""A class to structure the retrieving of information"""
	def __init__(self):
		"""Returns instance of the DataSource"""
		self.base_url = "http://www.namistt.com/DocumentLibrary/Market%20Reports"
		self.months = [
			"January",
			"February",
			"March",
			"April",
			"May",
			"June",
			"July",
			"August",
			"September",
			"October",
			"November",
			"December"]
		
		self.categories = [
			"root crops",
			"condiments and spices",
			"leafy vegetables",
			"vegetables",
			"fruits",
			"citrus"
		]
		
		self.category = "ROOT CROPS"  # The first category in the file
		
		self.type = "daily"
		self.start_row = 10
		self.url = ""
		self.prefix = "base"
		self.valid_list_path = "{0}/data/{1}_{2}_valid_url_list.json".format(dir_path,self.prefix, self.type)
		self.min_year = 2012
		self.max_year = datetime.now().year + 1
		
	def traverse_workbook(self, url):
		"""Traverse workbook sheets and extract row data."""
		values = []
		data = requests.get(url).content
		wb = open_workbook(url, file_contents=data)
		for sheet in wb.sheets():  # TODO So far only one sheet has data
			for row in range(sheet.nrows):
				if row > self.start_row:
					row_data = self.process_rows(sheet, row)
					if row_data:
						values.append(row_data)
		return values
	
	def process_rows(self, sheet, row):
		"""Process each row in excel sheet. Row is either a category or a record."""
		if sheet.cell_type(row, 0) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK):
			return None
		else:
			# Check if the second column is empty then usually for the category listing
			if not sheet.cell(row, 1).value:
				val = sheet.cell(row, 0).value
				# Check if in the valid list of categories
				if val.lower() in self.categories:
					self.category = val.upper()
			else:
				return self.process_record(sheet, row, self.category)
	
	def process_record(self, sheet, row, category):
		record = {
			'commodity': sheet.cell_value(row, 0).encode('ascii').lower(),
			'category': category.encode('ascii'),
			'unit': sheet.cell_value(row, 1).encode('ascii'),
			'volume': sheet.cell_value(row, 3),
			'price': sheet.cell_value(row, 6)
		}
		if sheet.cell(row, 3) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or record['volume'] == '':
			record['volume'] = 0.0
		
		if sheet.cell(row, 6) in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) or record['price'] == '':
			record['price'] = 0.0
		
		return record
	
	def get_url_from_date(self, year, month, day):
		return "{0}%20{1}%20{2}%20{3}.xls".format(self.url, str(day), str(month), str(year))
	
	def get_all_dates(self):
		"""Retrieve all the valid URLs for actual data files from the server"""
		valid_dates = []
		# Check if there is a cached
		if os.path.exists(self.valid_list_path):
			with open(self.valid_list_path, "r") as json_file:
				valid_dates = json.load(json_file)
				json_file.close()
		else:
			for year in range(self.min_year, self.max_year):
				for month in self.months:
					for day in range(1, 32):
						try:
							if datetime(year, self.months.index(month)+1, day) <= datetime.now():
								url = self.get_url_from_date(year, month, day)
								resp = httplib2.Http().request(url, 'HEAD')
								print("URL: {0} Status:{1}".format(url,resp[0]['status']))
								if int(resp[0]['status']) == 200:
									valid_dates.append({
										'url': url,
										'year': year,
										'month': month,
										'day': day
									})
						except Exception, e:
							pass
			
			# Store the data retrieved in a cache
			with open(self.valid_list_path, "w") as json_file:
				json.dump(valid_dates, json_file)
				json_file.close()
		
		print("Found {0} valid urls".format(len(valid_dates)))
		return valid_dates
	
	def retrieve_record_by_date(self, year, month, day):
		url = self.get_url_from_date(year, month, day)
		data = self.traverse_workbook(url)
		return data
	
	def get_recent_dates(self, last_date):
		"""Get all the dates between current date and the date submitted as parameter"""
		valid_dates = []
		day = datetime.now().day
		month = self.months[datetime.now().month - 1]
		year = datetime.now().year
		years = range(last_date.year, year+1)
		if month == 1:
			month_names = self.months
		else:
			month_names = self.months[last_date.month : datetime.now().month ]
		for year in years:
			for month in reversed(month_names):
				for day in range(1, 32):
					try:
						if datetime(year, self.months.index(month)+1, day) <= datetime.now():
							url = self.get_url_from_date(year, month, day)
							resp = httplib2.Http().request(url, 'HEAD')
							print("URL: {0} Status:{1}".format(url,resp[0]['status']))
							if int(resp[0]['status']) == 200:
								valid_dates.append({
									'url': url,
									'year': year,
									'month': month,
									'day': day
								})
					except Exception, e:
						pass
		
		print("Found {0} valid urls".format(len(valid_dates)))
		return valid_dates
	
	
class NDNWMDaily(DataSource):
	"""A class to extract daily records from the Norris Deonarine Market"""
	def __init__(self):
		"""Returns instance of the NDNWMDaily"""
		DataSource.__init__(self)
		self.setup()
		
	def setup(self):
		"""Method to setup / initialize class specific variables"""
		self.prefix = "NDNWM"
		self.url = "{0}/Daily/Norris%20Deonarine%20NWM%20Daily%20Market%20Report%20-".format(self.base_url)
		self.valid_list_path = "{0}/data/{1}_{2}_valid_url_list.json".format(dir_path,self.prefix, self.type)


class DatabaseManager():

	def getCurrentDB(self):
		try:
			client = MongoClient("mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461")
			db = client.get_default_database()
			return db
		except Exception as e:
			logging.error(e)
		return None
	
if __name__ == "__main__":
	source = NDNWMDaily()
	# source.get_recent_dates(datetime(2017, 4, 1))
	# source.retrieve_record_by_date(2017, "May", 12)
	source.get_all_dates()