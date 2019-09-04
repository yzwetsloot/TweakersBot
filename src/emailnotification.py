import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

with open("../config/emailconfig.txt") as fh:
    password = fh.readline().strip()
    sender_email = fh.readline().strip()
    receiver_email = fh.readline().strip()

PORT = 465


def send_price_notification(product: dict) -> None:
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


def send_error_notification(err: str) -> None:
    text = f"Error occurred: {err}"
    html = f"""
        <html>
            <body>
                <h1>
                    Error {err} occurred
                </h1>
                <p>
                    Possible Captcha page presented.
                    Switched to next Cookie data in argument list. 
                </p>
            </body>
        </html>
    """
    send_email(text, html, "Program error occurred")


def send_email(text: str, html: str, subject: str) -> None:
    print("[LOG] Send email", end="\r")

    message = MIMEMultipart("Alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("[LOG] Email sent")
