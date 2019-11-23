from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import smtplib
import ssl

logger = logging.getLogger(__name__)

with open("../config/config.json") as config:
    data = json.load(config)["email_config"]


def price_notification(product: dict) -> None:
    text = str(product)
    html = f"""
        <html>
            <body>
                <p>
                    <a href="{product["link"].strip()}">{product["link"]}</a>
                </p>
                <p>
                    Ad price is {product["price"]}
                </p>
                <h4>Relative to pricewatch price</h4>
                <p>
                    Absolute price difference is {product["price_difference"][0]}
                </p>
                <p>
                    Relative price difference is {product["price_difference"][1]}%
                </p>
                <h4>Relative to other sellers</h4>
                <p>
                    Absolute price difference is {product["price_difference"][2]}
                </p>
                <p>
                    Relative price difference is {product["price_difference"][3]}%
                </p>
                <h4>All prices</h4>
                <p>
                    {("{} " * len(product["price_old"])).format(*sorted(product["price_old"]))}
                </p>
            </body>
        </html>
    """
    send_email(text, html, "Significant price difference")


def send_email(text: str, html: str, subject: str) -> None:
    message = MIMEMultipart("Alternative")
    message["Subject"] = subject
    message["From"] = data["sender"]
    message["To"] = data["receiver"]

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", data["port"], context=context) as server:
        try:
            server.login(data["sender"], data["password"])
            server.sendmail(data["sender"], data["receiver"], message.as_string())
        except (smtplib.SMTPDataError, smtplib.SMTPAuthenticationError):
            logger.error("Email error occurred")
        except smtplib.SMTPException:
            logger.critical("Error occurred", exc_info=1)
