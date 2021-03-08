import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google_auth import get_google_service
from main import config


def send_mail(email_subject: str, body_text: str):
    service = get_google_service()
    if service is not None:
        try:
            recipients_list = config["EMAIL_SENDER"]["email_receivers"].split(",")
            for recipient in recipients_list:
                message = MIMEMultipart()
                message['to'] = recipient
                message['from'] = config["EMAIL_SENDER"]["email_sender"]
                message['subject'] = email_subject

                msg = MIMEText(body_text, "plain")
                message.attach(msg)

                b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
                b64_string = b64_bytes.decode()
                test_message = {'raw': b64_string}

                message = (service.users().messages().send(userId=config["GOOGLE_AUTH"]["user_id"], body=test_message)
                           .execute())
                print('Message Id: %s' % message['id'])
                return message
        except Exception as error:
            print('An error occurred: %s' % error)
