# ! /usr/bin/python

import smtplib
import configparser
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
config = configparser.ConfigParser()
config.read(os.path.join(base_path, "config.ini"))


def send_mail(recipient):
    recipients_list = [recipient]
    for recipient in recipients_list:
        sender = config["EMAIL_SENDER"]["email_sender"]
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Craigs list notification"
        msg['From'] = sender
        msg['To'] = recipient

        text = """\
        hello, 
        I am Interested in your listing. Please reply with the VIN# for this vehicle"""

        part = MIMEText(text, "plain")
        msg.attach(part)
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender, config["DATA_SOURCE"]["email_password"])
        mail.sendmail(sender, recipient, msg.as_string())
        mail.quit()