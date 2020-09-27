import smtplib
from email.mime.text import MIMEText
import mysql.connector as mcdb

def sendMail(sub,to_name,msg):
    mail_message = MIMEText("")
    mail_message['Subject'] = sub
    mail_message['From'] = "Truba TG-no-reply <no-reply@gmail.com>"
    mail_message['To'] = to_name
    smtp_session.sendmail("no-reply", to_name, mail_message.as_string()+msg) 

conn = mcdb.connect(host="localhost", user="root", passwd="", database="TG")
cursor = conn.cursor()
#cursor.close()
#conn.close()

print("pinfo connected to database")

smtp_session = smtplib.SMTP('smtp.gmail.com', 587) 
smtp_session.starttls() 
smtp_session.login("tgtruba@gmail.com","mytest21mail")
#smtp_session.quit()


print("pinfo connected to mailserver")


