import smtplib
import os 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from poker_scraper.config import config

def send_email(recipient_email_address, subject, body, file_attachment = None, file_name: str = None):
   try:
      msg = MIMEMultipart()
      msg["From"] = config.FROM_EMAIL_ADDRESS
      msg["To"] = recipient_email_address
      msg["Subject"] = subject
      msg.attach(MIMEText(body, 'plain'))

      if file_attachment is not None:
         attachment = MIMEText(file_attachment.read())
         attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
         msg.attach(attachment)

      with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
         server.starttls()
         server.login(config.FROM_EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD)
         server.sendmail(config.FROM_EMAIL_ADDRESS, recipient_email_address, msg.as_string())
   except Exception as e:
      print(f"Error sending email: {e}")
