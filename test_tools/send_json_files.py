import json
import os
import sys
import zlib
import requests
import gzip
import urllib.request

ENDPOINT_URL = 'http://54.91.231.144/posts/predict'
script_path = os.path.dirname(sys.argv[0])
files_path = os.path.join(script_path, "test_files")
print(files_path)
test_files = os.listdir(files_path)
"""for file in test_files:
    if "20190517-183003_HUB_OFICINA15" in file:
        print(file)
        with open(os.path.join(files_path, file)) as json_file:
            json_data = json.loads(json_file.read())

        json_data = {'data': json_data, 'hub':json_data[0]['HUB']}
        response = requests.post(ENDPOINT_URL, json=json_data)
        print(response.status_code)
"""


for file in test_files:
    #if "20190517-183003_HUB_OFICINA15" in file:
    print(file)
    with open(os.path.join(files_path, file)) as json_file:
        json_data = json.loads(json_file.read())
    data_to_send = json.dumps(json_data, default=str)
    print('>>> ' + str(sys.getsizeof(data_to_send)))
    compressed_data_to_send = zlib.compress(data_to_send.encode("UTF-8"))
    #compressed_data_to_send = zip_payload(data_to_send)
    print('>>> ' + str(sys.getsizeof(compressed_data_to_send)))
    print("sending %s"%(file))
    #header = {'Content-Encoding': 'gzip'}
    response = requests.post(ENDPOINT_URL, data=compressed_data_to_send)
    print('response.status_code:' + str(response.status_code))