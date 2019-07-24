import json
import os
import sys
import requests

ENDPOINT_URL = 'http://54.91.231.144/posts/predict'
script_path = os.path.dirname(sys.argv[0])
files_path = os.path.join(script_path, "test_files")
print(files_path)
test_files = os.listdir(files_path)
for file in test_files:
    with open(os.path.join(files_path, file)) as json_file:
        json_data = json.loads(json_file.read())
    data_to_send = json.dumps(json_data, default=str)
    print("sending %s"%(file))
    response = requests.post(ENDPOINT_URL, data=data_to_send)
    print('response.status_code:' + str(response.status_code))