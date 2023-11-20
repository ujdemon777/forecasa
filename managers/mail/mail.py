import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv, find_dotenv
import os
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from .template import message

_ = load_dotenv(find_dotenv())


sender_email = os.getenv("SENDER_EMAIL")
password = os.getenv("MAIL_APP_PASSWORD")
port = os.getenv("PORT")
mail_server = os.getenv("SERVER")


server = smtplib.SMTP(mail_server, port)
server.starttls()



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
            return JSONResponse({"msg": f"Email has been sent to {rec_email}","status_code":200})

        except smtplib.SMTPAuthenticationError as e:
            raise HTTPException(status_code=401, detail=str(e))

        finally:
            server.quit()

