def mandar_mail_notificacion(mail_text, To):
	import smtplib
	From = 'kazoohubs@kazoo.com.uy'
	Subject = "Error en servidor ML"
	smtp = smtplib.SMTP('smtp.gmail.com','587')
	smtp.ehlo()
	smtp.starttls()
	smtp.login('kazoohubs@kazoo.com.uy', 'kazooalarmas')
	BODY = '\r\n'.join(['To: %s' % To,
					'From: %s' % From,
                    'Subject: %s' % Subject,
                    '', mail_text])
	try:
		smtp.sendmail(From, [To], BODY)
		print ('email sent')
	except Exception as e:
		print ('error sending mail')
		print(e)

def missing_hubs_PCSEST():
	import os
	from flaskr import model_settings
	PCSEST = ["PCSEST_A1_8", "PCSEST_A1_9", "PCSEST_A1_MEDIO", "PCSEST_A2_1",
        "PCSEST_A2_3", "PCSEST_B1_19", "PCSEST_B1_20", "PCSEST_B1_21",
		"PCSEST_B1_23", "PCSEST_C1_10", "PCSEST_C1_11", "PCSEST_C1_24",
		"PCSEST_C2_4", "PCSEST_C2_6", "PCSEST_E1_MEDIO", "PCSEST_E2_17",
		"PCSEST_E2_CRUZADO", "PCSEST_E3_14", "PCSEST_E3_ENTRADA",
		"PCSEST_EURO_N1", "PCSEST_EURO_N2"]
	files = os.listdir(model_settings.predict_data_path)
	missing_hubs = []
	for hub in PCSEST:
		if any(hub in file for file in files):
			pass
			#si no hay archivos JSON de un Hub que tendria que haber se guarda su nombre en missing_hubs
		else:
			missing_hubs.append(hub)
			print(hub)
	return missing_hubs
