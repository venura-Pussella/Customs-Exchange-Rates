import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
import os
from dotenv import load_dotenv
load_dotenv()

def send_email(body: str):
    """Sends email with given body (other parameters defined in the function itself).

    Args:
        body (str): email body
    """

    # SMTP configuration
    SMTP_SERVER = "smtp.gmail.com" 
    SMTP_PORT = 587  # Typically 587 for TLS or 465 for SSL
    EMAIL_ADDRESS = "datapipelinebrowns@gmail.com" 
    EMAIL_PASSWORD = os.getenv('EMAIL_APP_PASSWORD')

    # Email details
    to_emails = ["rehangag@brownsgroup.com","venurap@brownsgroup.com","rehanga@live.com"]
    subject = "Customs ER Collector Message"

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ', '.join(to_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server and start TLS
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection

        # Log in to the email account
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        # Send the email
        server.sendmail(EMAIL_ADDRESS, to_emails, msg.as_string())

        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email: {e}")
        print(traceback.format_exc())

    finally:
        # Close the server connection
        server.quit()