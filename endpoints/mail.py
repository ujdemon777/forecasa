from fastapi import APIRouter, Depends, Request, HTTPException, Query, Body
from Oauth import create_access_token,get_current_user
from models.response import Response,ErrorResponse
from dotenv import load_dotenv, find_dotenv
from models import schema
from managers.mail.mail import Email

_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/mail",
    tags=["Mail"],
    responses={404: {"description": "Not found"}},
)


@router.post("/send-email")
async def request_verification_code(email_verification_request: schema.EmailVerificationRequest):
    rec_email = email_verification_request.email
    try:
        mail_sent = await Email.sendMail(rec_email)
        print(mail_sent)
        if mail_sent:
            return {"message": "Verification email sent successfully"}  
        else:
            return ErrorResponse("error occurred while sending verification mail", 500, str(e)) 
    except Exception as e:
        return ErrorResponse("error occurred while sending verification mail", 500, str(e))