import os
from flaskr import model_settings

print("Create train data directory")
os.system("mkdir " + model_settings.train_data_path[:-1])
print("Create predict data directory")
os.system("mkdir " + model_settings.predict_data_path[:-1])
print("Create logs directory")
os.system("mkdir " + model_settings.LOG_FILE[0:-12])
print("Create log file")
os.system("touch " + model_settings.LOG_FILE)
