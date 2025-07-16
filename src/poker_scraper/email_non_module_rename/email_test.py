import smtplib
import os 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
FROM_EMAIL_ADDRESS = os.getenv("emailAddressForSmtpClient")
EMAIL_APP_PASSWORD = os.getenv("SMTPAppKeyForEmailClient")
print(EMAIL_APP_PASSWORD)
print(FROM_EMAIL_ADDRESS)
RECIPIENT_EMAIL = "jaxonallsage@gmail.com"

def send_email(recipient_email_address, subject, body):
   try:
      msg = MIMEMultipart()
      msg["From"] = FROM_EMAIL_ADDRESS
      msg["To"] = recipient_email_address
      msg["Subject"] = subject
      msg.attach(MIMEText(body, 'plain'))

      with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
         server.starttls()
         server.login(FROM_EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
         server.sendmail(FROM_EMAIL_ADDRESS, recipient_email_address, msg.as_string())
         print("Email sent successfully")
   except Exception as e:
      print(f"Error sending email: {e}")

if __name__ == "__main__":
   send_email(RECIPIENT_EMAIL, "Sample Subject", "sample body")