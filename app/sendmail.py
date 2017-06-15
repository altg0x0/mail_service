import smtplib
from email.mime.text import MIMEText
from email.header    import Header

from flask_login import current_user

def send(to, fro, subject, body):
    smtp_host = '127.0.0.1'  # yahoo
    recipients_emails = to

    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = fro
    msg['To'] = to

    s = smtplib.SMTP(smtp_host, 587, timeout=10)
    s.set_debuglevel(1)
    try:
        s.starttls()
        s.sendmail(msg['From'], recipients_emails, msg.as_string())
        msg.as_string
    finally:
        s.quit()
