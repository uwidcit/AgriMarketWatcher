from datetime import timedelta
from flask import make_response, request, current_app, Flask
from functools import update_wrapper
import os


app = Flask(__name__)
app.debug = True





if __name__ == "__main__":
	port = int(os.environ.get("PORT", 5000))
	# app.run(host = '127.0.0.1', port = port)
	app.run(host='0.0.0.0', port=port)