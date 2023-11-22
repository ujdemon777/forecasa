from fastapi import APIRouter, HTTPException, Body, Depends
from Oauth import create_access_token
from models.user import User
from config.db import Database
from schemas.auth import CreateUserSchema
from datetime import datetime
from utils import hash_password,verify_password
from typing import Annotated
from Oauth import get_current_user


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)


@router.post('/register')
async def create_user(payload: CreateUserSchema):
 
    user = session.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        raise HTTPException(status_code=409,
                            detail='Account already exist')
    
    try:
        payload.email = payload.email.lower()
        payload.password = hash_password(payload.password)
        payload.created_at = datetime.utcnow()
        payload.updated_at = datetime.utcnow()
        new_user = User(**payload.model_dump())

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return {"msg": "User registered successfully", "user_id": new_user.id}

    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))


@router.post('/login',response_model=None)
def login(user_detail: dict = Body(..., description="requires email and password")):

    email = user_detail.get('email')
    password = user_detail.get('password')

    if not email or not password:
        raise HTTPException(status_code=401,
                            detail='Need Both Email and Password')

    user = session.query(User).filter(User.email == email.lower()).first() 
    if not user:
        raise HTTPException(status_code=401,
                            detail='Incorrect Email or Password')

    if not verify_password(password, user.password):
        raise HTTPException(status_code=401,
                            detail='Incorrect Password')

    access_token = create_access_token(data={"user_id":user.id})
    return {"msg":"bearer token generated","token":access_token}





@router.get('/me')
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {"user":current_user}