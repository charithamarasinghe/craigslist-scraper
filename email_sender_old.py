import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from main import config


def send_mail(email_subject: str, body_text: str):
    recipients_list = [config["EMAIL_SENDER"]["email_receiver"]]
    for recipient in recipients_list:
        sender = config["EMAIL_SENDER"]["email_sender"]
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_subject
        msg['From'] = sender
        msg['To'] = recipient

        text = body_text

        part = MIMEText(text, "plain")
        msg.attach(part)
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login(sender, config["DATA_SOURCE"]["email_password"])
        mail.sendmail(sender, recipient, msg.as_string())
        mail.quit()
