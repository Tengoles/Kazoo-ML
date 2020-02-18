from django.test import TestCase
import requests
import zlib
from datetime import datetime
import json
import sys

# Create your tests here.
def process_file(filepath):
    data_cruda = []
    with open(filepath) as file:
        #print(file)
        for index, line in enumerate(file.read().splitlines()):
            if '\x00' in line:
                print('null character in line')
                continue
            splited_line = line.split()
            if len(splited_line) != 5:
                print('short/long line')
                continue
            try:
                fechahora = datetime.strptime(splited_line[0] + " " + splited_line[1], "%Y-%m-%d %H:%M:%S.%f")
                MAC = splited_line[2]
                RSSI = int(splited_line[3])
                HUB = splited_line[4]
                dict = {'fechahora':fechahora, 'MAC':MAC, 'RSSI':RSSI, 'HUB':HUB}
                data_cruda.append(dict)

            except Exception as e:
                print(str(e))
                pass
    return data_cruda
    
def test_store_json_compressed(ENDPOINT_URL="http://127.0.0.1:8000/store_json"):
    data_to_send = process_file("test_data.txt")
    data_to_send2 = json.dumps(data_to_send, default=str)
    compressed_data_to_send = zlib.compress(data_to_send2.encode("UTF-8"))
    print('>>> ' + str(sys.getsizeof(data_to_send2)))
    print("sending data")
    response = requests.post(ENDPOINT_URL, data=compressed_data_to_send)
    print('>>> ' + str(sys.getsizeof(compressed_data_to_send)))
    print(response.status_code)

def test_store_json(ENDPOINT_URL="http://127.0.0.1:8000/store_json"):
    data_to_send = process_file("test_data.txt")
    data_to_send2 = json.dumps(data_to_send, default=str)
    print("sending data")
    response = requests.post(ENDPOINT_URL, data=data_to_send2)
    print(response.status_code)


if __name__ == "__main__":
    test_store_json()
    test_store_json_compressed()

    
