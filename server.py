# Import libraries
#import numpy as np
#import pandas as pd
from flask import Flask, request, jsonify
import time
import json
import model_settings
#import pickle
app = Flask(__name__)

@app.route('/train',methods=['POST'])
def receive_data():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    print("Data received")
    dirPATH = model_settings.train_data_path
    with open(dirPATH + time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json', 'a') as fout:
        json.dump(data, fout)
    app.logger.info('%s train data received successfully', time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json')
    return "JSON Received and stored!", 200


@app.route('/predict', methods=['POST'])
def process_file():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    print("Data received")
    dirPATH = model_settings.predict_data_path
    with open(dirPATH + time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json', 'a') as fout:
        json.dump(data, fout)
    app.logger.info('%s predict data received successfully', time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json')
    return "JSON Received and stored!", 200

if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='messages.log',level=logging.DEBUG)
    app.run(host="0.0.0.0", port=5000)
	#app.run(port=5000, debug=True)
