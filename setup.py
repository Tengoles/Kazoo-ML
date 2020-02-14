import os
import subprocess

def touch(path):
	with open(path, 'a'):
		os.utime(path, None)
os.system("pip install -r requirements.txt")
BASE_DIR = str(os.path.dirname(os.path.abspath(__file__)))
try:
	os.mkdir(os.path.join(BASE_DIR, "predict_data"))
	print('Directory %s created.'%(str(os.path.join(BASE_DIR, "predict_data"))))
except FileExistsError as e:
	print('Directory %s not created.'%(str(os.path.join(BASE_DIR, "predict_data"))))

try:
	os.mkdir(os.path.join(BASE_DIR, "logs"))
	print('Directory %s created.'%(str(os.path.join(BASE_DIR, "logs"))))
except FileExistsError as e:
	print('Directory %s not created.'%(str(os.path.join(BASE_DIR, "logs"))))

touch(os.path.join(BASE_DIR, "logs", "general_log.log"))

#os.system("%s python manage.py makemigrations"%(os.path.join(BASE_DIR, "Kazoo_ML_root")))
#os.system("%s python manage.py migrate"%(os.path.join(BASE_DIR, "Kazoo_ML_root")))
#os.system("%s python manage.py collectstatic"%(os.path.join(BASE_DIR, "Kazoo_ML_root")))
#subprocess.Popen(os.path.join(BASE_DIR, "Kazoo_ML_root", "python manage.py makemigrations"))

