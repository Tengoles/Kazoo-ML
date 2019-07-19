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

