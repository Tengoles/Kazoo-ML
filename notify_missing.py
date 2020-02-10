import server_tools
from datetime import datetime, timedelta
import ml_settings


missing_hubs = server_tools.missing_hubs_PCSEST()
with open(model_settings.LOG_FILE, "a") as logFile:
	logFile.write("%s Check de actividad de Hubs: "%(str(datetime.now())))
if len(missing_hubs) > 0:
	date = str(datetime.now() - timedelta(hours=3))[0:10]
	time = str(datetime.now() - timedelta(hours=3))[11:16]
	message = "El %s a las %s faltaron estos Hubs:\n"%(date, time)
	for hub in missing_hubs:
		message = message + hub + "\n"
	for mail in ml_settings.notification_mails:
		server_tools.mandar_mail_notificacion(message, mail)
	with open(model_settings.LOG_FILE, "a") as logFile:
		logFile.write(message + "\n")
	print(message)
else:
	with open(model_settings.LOG_FILE, "a") as logFile:
		 logFile.write("No hay Hubs inactivos")
