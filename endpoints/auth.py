from fastapi import APIRouter, Depends, Request, HTTPException, Query, Body
from Oauth import create_access_token,get_current_user
from models.response import Response,ErrorResponse
from dotenv import load_dotenv, find_dotenv
from models.model import User
from config.db import Database
from pydantic import EmailStr
from models import schema
from datetime import datetime
from utils import hash_password,verify_password
from typing import Annotated


_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/auth",
    tags=[""],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)


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

    # new_user = User(
    #     email=payload.email.lower(), 
    #     password=payload.password,  
    #     role='user',
    #     created_at = datetime.utcnow(),
    #     updated_at = datetime.utcnow()
    # )

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


@router.get('/user', response_model=schema.UserBaseSchema)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

