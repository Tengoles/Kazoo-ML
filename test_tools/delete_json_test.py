import os

received_files_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
received_files_path = os.path.join(received_files_path, "flaskr")
received_files_path = os.path.join(received_files_path, "predict_data")
print(received_files_path)
#en received_files_path tengo el path para los archivos que el servidor recibe y todavia no proceso

script_path = os.path.dirname(os.path.abspath(__file__))
files_path = os.path.join(script_path, "test_files")
test_files = os.listdir(files_path) #en test_files tengo los nombres de los archivos que se mandan para hacer test
#print(test_files)
for file in test_files:
    print("Deleting: %s"%(os.path.join(received_files_path, file)))
    os.remove(os.path.join(received_files_path, file))
