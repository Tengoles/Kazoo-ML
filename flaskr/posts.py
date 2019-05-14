from flask import Blueprint, request, current_app
from . import model_settings
import json
import time

bp = Blueprint('posts', __name__, url_prefix='/posts')
import logging
logging.basicConfig(filename=model_settings.LOG_FILE, level=logging.DEBUG)

@bp.route('/train',methods=['POST'])
def receive_data():
    # Get the data from the POST request
    data = request.get_json(force=True)
    print("Data received")
    dirPATH = model_settings.train_data_path
    with open(dirPATH + time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json', 'a') as fout:
        json.dump(data, fout)
    current_app.logger.info('%s train data received successfully', time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json')
    return "JSON Received and stored!", 200

@bp.route('/predict', methods=['POST'])
def process_file():
    # Get the data from the POST request.
    data = request.get_json(force=True)
    print("Data received")
    dirPATH = model_settings.predict_data_path
    with open(dirPATH + time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json', 'a') as fout:
        json.dump(data, fout)
    current_app.logger.info('%s predict data received successfully', time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json')
    return "JSON Received and stored!", 200
