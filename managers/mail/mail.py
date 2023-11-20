import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv
import os

_ = load_dotenv(find_dotenv())


sender_email = os.getenv("SENDER_EMAIL")
password = os.getenv("MAIL_APP_PASSWORD")
port = os.getenv("PORT")
mail_server = os.getenv("SERVER")


server = smtplib.SMTP(mail_server, port)
server.starttls()



verification_link = "https://example.com/verify?token=your_verification_token"

# Construct the HTML email message with the verification link
message = f"""
<html>
<head></head>
<body>
    <p>Dear user,</p>
    <p>Thank you for signing up. Please click the following link to verify your email:</p>
    <a href="{verification_link}">Verify Email</a>
    <p>If the link doesn't work, copy and paste the following URL into your browser:</p>
    <p>{verification_link}</p>
</body>
</html>
"""


class Email:
    
    @classmethod
    async def sendMail(cls,rec_email):
        try:
            server.login(sender_email, password)
            print("Login success")

            msg = MIMEText(message, "html")
            msg["Subject"] = "Your verification code (Valid for 10min)"
            msg["From"] = sender_email
            msg["To"] = rec_email

            server.sendmail(sender_email, rec_email, msg.as_string())
            print("Email has been sent to", rec_email)

        except smtplib.SMTPAuthenticationError as e:
            print("Login failed:", e)

        finally:
            server.quit()

