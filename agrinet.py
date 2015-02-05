from flask import Flask, request, jsonify, make_response, url_for,render_template, current_app
from flask.ext.pymongo import PyMongo
from bson import json_util, objectid
from datetime import datetime, timedelta
import re#regular expression
import os

from functools import update_wrapper

app = Flask(__name__)
app.debug = True

app.config['MONGO_URI'] = "mongodb://agriapp:simplePassword@ds043057.mongolab.com:43057/heroku_app24455461"
# app.config['MONGO_URI'] = "mongodb://localhost/agrinet";
mongo = PyMongo(app)


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True,automatic_options=True):
	if methods is not None:
		methods = ', '.join(sorted(x.upper() for x in methods))
	if headers is not None and not isinstance(headers, basestring):
		headers = ', '.join(x.upper() for x in headers)
	if not isinstance(origin, basestring):
		origin = ', '.join(origin)
	if isinstance(max_age, timedelta):
		max_age = max_age.total_seconds()

	def get_methods():
		if methods is not None:
			return methods

		options_resp = current_app.make_default_options_response()
		return options_resp.headers['allow']

	def decorator(f):
		def wrapped_function(*args, **kwargs):
			if automatic_options and request.method == 'OPTIONS':
				resp = current_app.make_default_options_response()
			else:
				resp = make_response(f(*args, **kwargs))
			if not attach_to_all and request.method != 'OPTIONS':
				return resp

			h = resp.headers
			h['Access-Control-Allow-Origin'] = origin
			h['Access-Control-Allow-Methods'] = get_methods()
			h['Access-Control-Max-Age'] = str(max_age)
			h['Access-Control-Allow-Credentials'] = 'true'
			h['Access-Control-Allow-Headers'] = \
				"Origin, X-Requested-With, Content-Type, Accept, Authorization"
			if headers is not None:
				h['Access-Control-Allow-Headers'] = headers
			return resp

		f.provide_automatic_options = False
		return update_wrapper(wrapped_function, f)
	return decorator

#Helper/Utility functions
def convert_compatible_json(crop):
	crop["date"] = crop["date"].strftime('%Y-%m-%dT%H:%M:%S')	#convert the date object to a string
	crop["id"] = str(crop["_id"])													#convert mongodb id to a string
	del crop["_id"] 																			#remove original key
	return crop

def process_results(cursor):									
	res = []
	for c in cursor:											#Iterates through each result from the mongodb result cursor
		res.append(convert_compatible_json(c))					#Pushes (appends) result to a list of results
	return res

def format_crop_query(crop):
	return {"commodity" : crop}

def format_category_query(category):
	qry = [];
	category = category.upper().split(",")
	for c in category:
		qry.append({"category": re.compile(c,  re.IGNORECASE)})
	
	res = {"$or":qry} if (len(qry) > 1) else qry[0] 					#http://en.wikipedia.org/wiki/Conditional_operator#Python
	return res

def process_options(options, request):
	if (len(request.args) > 0):
		if request.args.get("crop"):
			options['commodity'] = re.compile(str(request.args.get("crop")), re.IGNORECASE)#convert to case insensitive search for crop name
		if request.args.get("commodity"):
			options['commodity'] = re.compile(str(request.args.get("commodity")), re.IGNORECASE)
		if request.args.get("category"):
			options.update(format_category_query(request.args.get("category")))
		if request.args.get("date"):
			try: 																						#check if the date is either in one of the two supported formats
				options['date'] = datetime.strptime(str(request.args.get('date')), '%Y-%m-%dT%H:%M:%S')
			except ValueError:
				options['date'] = datetime.strptime(str(request.args.get('date')), '%Y-%m-%d')

	if len(options) > 1:																#if more than one dimension added we perform an or operation as opposed to an and
		qry = []
		for key in options.keys():
			print key
			qry.append({key: options[key]})									#convert the dictionary to a list of dictionaries
		options = {"$or": qry}														#combine each dictionary in the list to a single dictionary combined with or operator
	
	return options

# Display Pages	
@app.route("/")
@crossdomain(origin='*')
def home():
	links = []
	return render_template("main.html")

@app.route("/about")
def about():
	return render_template("about.html")

# Meta API
#Returns the list of crops available
@app.route('/crops/crops')
@app.route('/crops')
@crossdomain(origin='*')
def crops_list():
	crops = []
	crops = mongo.db.daily.distinct("commodity")
	return json_util.dumps(crops)

@app.route('/crops/categories')													# Returns the list of categories to which crops can belong
@app.route('/crops/categories/<category>')							# Returns the crops that belong to the category
@crossdomain(origin='*')
def crop_categories(category = None):
	res = []
	if category:
		res = mongo.db.daily.find({"category":category.upper()}).distinct("commodity")
	else:
		res = mongo.db.daily.distinct("category")
	return json_util.dumps(res)


# Daily API
@app.route('/crops/daily')															#Returns all the daily priceses
@app.route('/crops/daily/<id>')													#Returns the daily price for a sepcific crop
@crossdomain(origin='*')
def crops_id(id=None):
	res = []
	options = {}
	offset = 0
	limit = 10
	try:
		if id:
			crops = mongo.db.daily.find({"_id":objectid.ObjectId(id)})
		else:
			if len(request.args) > 0:
				if request.args.get("limit"):								#Check limit to determine how much records to return
					limit = int(request.args.get("limit"))
				if request.args.get("offset"):								#Check offset to determine which record to start from
					offset = int(request.args.get("offset"))

			options = process_options(options, request)
			crops = mongo.db.daily.find(options).sort( "date" , -1 ).skip(offset).limit(limit)
		res = process_results(crops)
	except Exception, e:
		print e
	
	return json_util.dumps(res,default=json_util.default)

@app.route("/crops/daily/dates") 												#returns all the daily dates available
@app.route("/crops/daily/dates/<date>")									#returns the commodities for the date specified
@crossdomain(origin='*')
def daily_dates_list(date = None):
	res = []
	options = {}
	offset = 0
	limit = 10
	try:
		if date:
			try: 																						#check if the date is either in one of the two supported formats
				options['date'] = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
			except ValueError:
				options['date'] = datetime.strptime(date, '%Y-%m-%d')
		
			if len(request.args) > 0:
				if request.args.get("limit"):										#Check limit to determine how much records to return
					limit = int(request.args.get("limit"))
				if request.args.get("offset"):									#Check offset to determine which record to start from
					offset = int(request.args.get("offset"))


			options = process_options(options, request)
			crops = mongo.db.daily.find(options).sort( "date" , -1 ).skip(offset).limit(limit)
			res = process_results(crops)


		else:
			end = datetime.now()
			start = end - timedelta(days=30) 								#default to 30 days difference
			options = {"date":{'$gte': start, '$lt': end}} 	#between dates syntax for mongodb
			dates = mongo.db.daily.find(options).distinct("date")	
			res = map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'), dates)
			return json_util.dumps(res)

		
			

			
	


	except Exception, e:
		print e

	return json_util.dumps(res)

@app.route('/crops/daily/recent')												# Returns the daily prices of the most recent entry
@app.route('/crops/daily/recent/<crop>')								# Returns the most recent daily price of the specified comodity
@crossdomain(origin='*')
def most_recent_daily_data(crop = None):
	if crop:
		crops = mongo.db.dailyRecent.find(format_crop_query(crop)) 	# If we have a crop that we want to obtain
	else:
		crops = mongo.db.dailyRecent.find() 								# Else, if we want all crops
	result = process_results(crops)
	return json_util.dumps(result, default =  json_util.default) 


@app.route('/crops/daily/category')
@app.route('/crops/daily/category/<category>')
@crossdomain(origin='*')
def crop_daily_categories(category=None):
	res = []
	options = {}
	offset = 0
	limit = 10

	if len(request.args) > 0:
		if request.args.get("limit"):											#Check limit to determine how much records to return
			limit = int(request.args.get("limit"))
		if request.args.get("offset"):										#Check offset to determine which record to start from
			offset = int(request.args.get("offset"))

	if category:
		options = process_options( format_category_query(category), request)
		crops = mongo.db.daily.find(options).sort( "date" , -1 ).skip(offset).limit(limit)
		res = process_results(crops)
	else:
		res = mongo.db.daily.distinct("category")

	return json_util.dumps(res,default=json_util.default)


@app.route('/crops/daily/commodity')
@app.route('/crops/daily/commodity/<commodity>')
@crossdomain(origin='*')
def crop_daily_commodity(commodity=None):
	res = []
	commodities = ["Carrot" , "Cassava" , "Yam (Local)" , "Yam (Imported)" , "Dasheen(Local) " , " Dasheen(Imported) " , " Eddoe (Local) " , " Eddoe (Imported) " , " Sweet Potato (Local) " , " Sweet Potato (Imported) " , " Ginger " , " Celery " , " Chive (L) " , " Thyme (s) " , " Hot Pepper (100's) " , " Hot Pepper (40 lb) " , " Shadon Beni " , " Pimento (S) " , " Pimento (M) " , " Pimento (L) " , " Lettuce (S) " , " Lettuce (M) " , " Lettuce (L) " , " Patchoi " , " Spinach (Amarantus spp.) " , " Cabbage (Imported) (Gn) " , " Cabbage(Local) (Gn) " , " Cabbage (White) " , " Cabbage (Imported) (Purple) " , " Callaloo Bush (Open) " , " Callaloo Bush (Roll) " , " Cauliflower(Imported) " , " Cauliflower (Local) " , " Bodi bean " , " Seim bean " , " Pigeon Pea " , " Cucumber " , " Melongene (S) " , " Melongene (M) " , " Melongene (L) " , " Ochro " , " Plantain (Green) " , " Plantain (Ripe) " , " Pumpkin " , " Sweet Pepper (S) " , " Sweet Pepper (M) " , " Sweet Pepper (L) " , " Sweet Pepper (Imported) " , " Tomato (S) " , " Tomato (M) " , " Tomato (L) " , " Tomato (Imported) " , " Caraillie (S) " , " Caraillie (M) " , " Caraillie (L) " , " Squash " , " Christophene " , " Coconut (Dry) (L) " , " Coconut (Dry) (S) " , " Coconut (Dry) (M) " , " Banana (Ripe) " , " Banana (Green) " , " Banana (Gr.Michel) " , " Paw Paw " , " Pineapple " , " Watermelon " , " Sorrel " , " Lime (S) " , " Lime (M) " , " Lime (L) " , " Grapefruit " , " Orange (S) " , " Orange (M) " , " Orange (L) " , " Orange (Navel) " , " Orange (King) " , " Portugal "]
	commodities = map(lambda x: x.strip().lower(), commodities)

	if commodity:
		commodity = commodity.lower().split(",")
		qry = []
		for c in commodity:
			qry.append({"commodity": c})
		crops = mongo.db.daily.find({"$or":qry})
		res = process_results(crops)

	return json_util.dumps(res,default=json_util.default)

@app.route('/crops/daily/predict')												# Returns the daily prices of the most recent entry
@app.route('/crops/daily/predict/<crop>')								# Returns the most recent daily price of the specified comodity
@crossdomain(origin='*')
def prediction_data(crop = None):
	if crop:
		crops = mongo.db.predictions.find({"name":crop}) 	# If we have a crop that we want to obtain
	else:
		crops = mongo.db.predictions.find() 								# Else, if we want all crops
	result = crops
	return json_util.dumps(result, default =  json_util.default)

#Monthly API

@app.route("/crops/monthly/dates")
@crossdomain(origin='*')
def monthly_dates_list():
	end = datetime.now()
	start = end - timedelta(days=300) 								#default to 30 days difference
	query = {"date":{'$gte': start, '$lt': end}} 					#between dates syntax for mongodb
	dates = mongo.db.monthly.find(query).distinct("date")				
	dates = map(lambda x: x.strftime('%Y-%m-%dT%H:%M:%S'), dates)
	return json_util.dumps(dates)

@app.route('/crops/monthly')
@app.route('/crops/monthly/<date>')
@crossdomain(origin='*')
def monthly_crops(date = None):
	res = []
	options = {}
	offset = 0
	limit = 10
	try:
		if date:
			if date != "all":												#if the date is all then no specified date query will return all
				try: 														#check if the date is either in one of the two supported formats
					options['date'] = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
				except ValueError:
					options['date'] = datetime.strptime(date, '%Y-%m-%d')
		else:
			d = datetime.now()
			d = d - timedelta(days=150)
			options['date'] = {'$gte': d, '$lt': datetime.now()}
		
		if len(request.args) > 0:
			if request.args.get("limit"):								#Check limit to determine how much records to return
				limit = int(request.args.get("limit"))
			if request.args.get("offset"):								#Check offset to determine which record to start from
				offset = int(request.args.get("offset"))

		options = process_options(options, request)
		crops = mongo.db.monthly.find(options).sort( "date" , -1 ).skip(offset).limit(limit)
		res = process_results(crops)
	except Exception, e:
		print e
	
	return json_util.dumps(res,default=json_util.default)
	

@app.route('/crops/monthly/category/')
@app.route('/crops/monthly/category/<category>')
@crossdomain(origin='*')
def monthly_crop_category(category = None):
	res = []
	options = {}
	offset = 0
	limit = 10

	try:
		if category:
			if len(request.args) > 0:
				if request.args.get("limit"):								#Check limit to determine how much records to return
					limit = int(request.args.get("limit"))
				if request.args.get("offset"):								#Check offset to determine which record to start from
					offset = int(request.args.get("offset"))

			options = process_options(options, request)
			options.update(format_category_query(category))				#merge the two dictionaries together				

			crops = mongo.db.daily.find(options).sort( "date" , -1 ).skip(offset).limit(limit)
			res = process_results(crops)
		else:
			res = mongo.db.monthly.distinct("category")
	except Exception, e:
		print e

	return json_util.dumps(res,default=json_util.default)

@app.route('/crops/monthly/commodity/')
@app.route('/crops/monthly/commodity/<commodity>')
@crossdomain(origin='*')
def monthly_crop_commodity(commodity = None):
	res = []
	options = {}
	offset = 0
	limit = 10
	qry = []

	try:
		if commodity:
			if len(request.args) > 0:
				if request.args.get("limit"):								#Check limit to determine how much records to return
					limit = int(request.args.get("limit"))
				if request.args.get("offset"):								#Check offset to determine which record to start from
					offset = int(request.args.get("offset"))

			options = process_options(options, request)

			commodity = commodity.lower().split(",")
			for c in commodity:
				qry.append({"commodity": c})
			
			options = options.update({"$or":qry})

			crops = mongo.db.daily.find(options).sort( "date" , -1 ).skip(offset).limit(limit)
			res = process_results(crops)
		else:
			res = mongo.db.monthly.distinct("commodity")
	except Exception, e:
		print e

	return json_util.dumps(res,default=json_util.default)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		do_the_login()
	else:
		show_the_login_form()

if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	# app.run(host = '127.0.0.1', port = port)
	app.run(host='0.0.0.0', port=port)
