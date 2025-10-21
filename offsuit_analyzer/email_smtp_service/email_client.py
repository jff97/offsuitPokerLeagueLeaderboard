import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from offsuit_analyzer.config import config

def send_email(recipient_email_address, 
               subject, 
               body, 
               text_file_attachment=None, 
               text_file_name: str = None, 
               binary_file_attachment=None, 
               binary_file_name=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = config.FROM_EMAIL_ADDRESS
        msg["To"] = recipient_email_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, 'plain'))

        if text_file_attachment is not None:
            text_file_attachment.seek(0)
            attachment = MIMEText(text_file_attachment.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=text_file_name)
            msg.attach(attachment)

        if binary_file_attachment is not None:
            binary_file_attachment.seek(0)
            attachment = MIMEApplication(binary_file_attachment.read(), Name=binary_file_name)
            attachment.add_header('Content-Disposition', 'attachment', filename=binary_file_name)
            msg.attach(attachment)

        with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.FROM_EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD)
            server.sendmail(config.FROM_EMAIL_ADDRESS, recipient_email_address, msg.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")
