from fastapi import APIRouter, HTTPException, Body, Depends
from Oauth import create_access_token
from models.user import User
from config.db import get_db
from schemas.user import CreateUserSchema
from datetime import datetime
from utils import hash_password,verify_password
from Oauth import get_current_user
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)


@router.post('/register')
async def create_user(payload: CreateUserSchema,db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == payload.email.lower()).first()
        if existing_user:
            raise HTTPException(status_code=409,
                                detail='Account already exist')
    
        payload.email = payload.email.lower()
        payload.password = hash_password(payload.password)
        payload.created_at = datetime.utcnow()
        payload.updated_at = datetime.utcnow()

        new_user = User(**payload.model_dump())

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"msg": "User registered successfully", "user_id": new_user.id}

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()


@router.post('/login')
def login(user_detail: dict = Body(..., description="requires email and password"),db: Session = Depends(get_db)):
    try:
        email = user_detail.get('email')
        password = user_detail.get('password')

        if not email or not password:
            raise HTTPException(status_code=401,
                                detail='Need Both Email and Password')

        user = db.query(User).filter(User.email == email.lower()).first() 
        if not user:
            raise HTTPException(status_code=401,
                                detail='Incorrect Email or Password')

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401,
                                detail='Incorrect Password')

        access_token = create_access_token(data={"user_id":user.id})
        return {"msg":"bearer token generated","token":access_token}
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()



@router.get('/me')
async def get_current_user(current_user: str = Depends(get_current_user)):
    try:
        if current_user:
            return {"user":current_user}
        
    except Exception as e:
        raise HTTPException(status_code=400,detail=f'user not found : {str(e)}')