from flask import Blueprint, request, current_app
from . import model_settings
import json
import time
import gzip
import zlib
#import StringIO

bp = Blueprint('posts', __name__, url_prefix='/posts')
import logging
logging.basicConfig(filename=model_settings.LOG_FILE, level=logging.DEBUG)

@bp.route('/predict', methods=['POST'])
def process_file():
    # Get the data from the POST request.
    dirPATH = model_settings.predict_data_path
    if request.is_json:
        data = request.get_json(force=True)
        filename = time.strftime("%Y%m%d-%H%M%S") + "_"  + data['hub'] + '.json'
        with open(dirPATH + filename, 'a') as fout:
            json.dump(data['data'], fout)
        current_app.logger.info('%s predict data received successfully', filename)
    else:
        print("request.is_json: " + str(request.is_json))
        data = request.data
        decompressed_data = zlib.decompress(data)
        data = json.loads(zlib.decompress(data).decode("UTF-8"))
        filename = time.strftime("%Y%m%d-%H%M%S") + "_"  + data[0]['HUB'] + '.json'
        with open(dirPATH + filename, 'a') as fout:
            json.dump(data, fout)
        current_app.logger.info('%s predict data received successfully', filename)
    return "JSON Received and stored!", 200
