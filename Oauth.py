from datetime import timedelta, datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import defer
from models.user import User
from config.db import get_db
from dotenv import load_dotenv, find_dotenv
import os
from sqlalchemy.orm import Session

import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

_ = load_dotenv(find_dotenv())

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

    

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt

def verify_token_access(token: str):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="You Are Not Authorized",
                                          headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        id: str = payload.get("user_id")
        if id is None:
            raise credentials_exception
    except JWTError as e:
        print(e)
        raise credentials_exception

    return payload

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    
    try:
        token = verify_token_access(token)
        user_id = token.get('user_id')

        if user_id is not None:
            user = db.query(User).options(defer(User.password)).filter(User.id == user_id).first()
            if user:
                return user
            else:
                raise HTTPException(status_code=404,detail=f'Invalid token, No user found')
        else:
            raise HTTPException(status_code=401, detail='Invalid token')

    except HTTPException as http_exception:
        raise http_exception        

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500,
                            detail=f'error:{str(e)}')
    
    finally:
        db.close()