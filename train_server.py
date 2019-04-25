# Import libraries
#import numpy as np
#import pandas as pd
from flask import Flask, request, jsonify
import time
import json
import model_settings
#import pickle
app = Flask(__name__)

@app.route('/api',methods=['POST'])
def receive_data():
    # Get the data from the POST request.
    if request.is_json:
	data = request.get_json(force=True)
	print("Data received")
	dirPATH = model_settings.train_data_path
	with open(dirPATH + time.strftime("%Y%m%d-%H%M%S") + data[0]['HUB'] + '.json', 'a') as fout:
	json.dump(data, fout)
	return "JSON Received and stored!", 200
    else:
	# The request body wasn't JSON so return a 400 HTTP status code
        return "Request was not JSON", 400	    
if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000)
	#app.run(port=5000, debug=True)
