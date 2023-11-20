from fastapi import APIRouter, Depends, Request, HTTPException, Query, Body
from Oauth import create_access_token,get_current_user
from models.response import Response,ErrorResponse
from dotenv import load_dotenv, find_dotenv
from models.model import User
from config.db import Database
from pydantic import EmailStr,BaseModel
from models import schema
from datetime import datetime
from utils import hash_password,verify_password
from typing import Annotated
import hashlib
from random import randbytes
# from mailersend import emails,templates
import os
from sqlalchemy.orm import defer
from sqlalchemy import desc



_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)


# mailersend_api_key = os.getenv('MAILERSEND_API_KEY')

@router.post('/register')
async def create_user(payload: schema.CreateUserSchema, request: Request):

    
    user_query = session.query(User).filter(
        User.email == payload.email.lower())
    user = user_query.first()
    if user:
        raise HTTPException(status_code=409,
                            detail='Account already exist')
    
    payload.email = payload.email.lower()
    payload.password = hash_password(payload.password)
    payload.created_at = datetime.utcnow()
    payload.updated_at = datetime.utcnow()
    new_user = User(**payload.dict())

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "User registered successfully", "user_id": new_user.id}



@router.post('/login',response_model=schema.Token)
def login(user_detail: dict = Body(..., description="email and password")):

    email = user_detail.get('email')
    password = user_detail.get('password')

    if not email or not password:
        raise HTTPException(status_code=400,
                            detail='Need Both Email and Password')

    user = session.query(User).filter(
       User.email == email.lower()).first() 
    if not user:
        raise HTTPException(status_code=400,
                            detail='Incorrect Email or Password')

    if not verify_password(password, user.password):
        raise HTTPException(status_code=400,
                            detail='Incorrect Email or Password')

    access_token = create_access_token(data={"user_id":user.id})
    return {"access_token":access_token,"token_type":"bearer","status": "success"}


@router.get('/current_user')
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

@router.post('/users')
async def read_all_users(
    page: int = Query(None, description="requires company id"),
    page_size: int = Query(None, description="require company id")):

    if not page:
        page=1

    if not page_size:
        page_size=50

    data = session.query(User).options(defer(User.password)).order_by(
        desc(User.created_at)).limit(page_size).offset((page-1)*page_size).all()
    return Response(data, "users retrieved successfully." , 200 , False)

@router.get('/{id}')
async def read_users(id:int):
    user = session.query(User).options(defer(User.password)).filter(User.id == id).first()
    
    if user:
        return {"data": user, "message": "User retrieved successfully.", "code": 200, "error": False}
    else:
        raise HTTPException(status_code=404, detail="User not found")


# mailer = emails.NewEmail(mailersend_api_key)
# template_id = 'pxkjn415800lz781'


# class EmailVerificationRequest(BaseModel):
#     email: EmailStr

# class EmailVerificationData:
#     def __init__(self, email, verification_code):
#         self.email = email
#         self.verification_code = verification_code

# verification_data = {}  

# @router.post("/request-verification-code")
# def request_verification_code(email_verification_request: EmailVerificationRequest):
#     mail_to = email_verification_request.email

#     mail_body = {}

#     mail_from = {
#         "name": "Ujjwal Kumar",
#         "email": "ujjwal@shorthillstech.com",
#     }

#     recipients = [
#         {
#             "name": "ujjwal",
#             "email": mail_to,
#         }
#     ]
    
    
#     variables = [
#     {
#         "email": mail_to,
#         "substitutions": [
#             {
#                 "var": "account.name",
#                 "value": ""
#             },
#             {
#                 "var": "support_email",
#                 "value": ""
#             }
#         ]
#     }
# ]


#     mailer.set_mail_from(mail_from, mail_body)
#     mailer.set_mail_to(recipients, mail_body)
#     mailer.set_subject("Hello from {$foo}", mail_body)
#     mailer.set_template("pxkjn415800lz781", mail_body)
#     mailer.set_simple_personalization(variables, mail_body)

#     response = mailer.send(mail_body)
#     print(response)

#     code = "123456"  
#     return {"message": "Verification code sent successfully"}


# @router.post("/verify-email")
# def verify_email(email: str, code: str):
#     stored_verification_data = verification_data.get(email)
#     if not stored_verification_data:
#         raise HTTPException(status_code=404, detail="Email not found")

#     if code == stored_verification_data.verification_code:
#         # Verification successful
#         return {"message": "Email verified successfully"}
#     else:
#         raise HTTPException(status_code=400, detail="Invalid verification code")
