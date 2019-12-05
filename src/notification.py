"""Functions for sending price notifications via e-mail"""
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import logging
import smtplib
import ssl
import time

logger = logging.getLogger(__name__)

with open("../config/config.json") as config:
    data = json.load(config)
    email_config = data["email_config"]

with open("../resources/template.html") as template:
    template = template.read()


def price_notification(**kwargs) -> None:
    text = str(kwargs)
    html = template.format(**kwargs)
    send_email("Significant price difference", text, html)


def send_email(subject, text, html) -> None:
    message = MIMEMultipart("Alternative")
    message["Subject"] = subject
    message["From"] = email_config["sender"]
    message["To"] = email_config["receiver"]

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", email_config["port"], context=context) as server:
        while True:
            try:
                server.login(email_config["sender"], email_config["password"])
                server.sendmail(email_config["sender"], email_config["receiver"], message.as_string())
            except (smtplib.SMTPDataError, smtplib.SMTPAuthenticationError):
                logger.error("Email error occurred")
                time.sleep(data["timeout"])
                continue
            except smtplib.SMTPException:
                logger.critical("Error occurred", exc_info=1)
            break
