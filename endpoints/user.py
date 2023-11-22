from fastapi import APIRouter, Depends, HTTPException, Query
from Oauth import get_current_user
from models.user import User
from config.db import Database
from typing import Annotated
from sqlalchemy.orm import defer
from sqlalchemy import desc



router = APIRouter(
    prefix="user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)



@router.get('/current_user')
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return {"current_user":current_user}


@router.get('/all')              
async def get_all_users(
    current_user: str = Depends(get_current_user),
    page: int = Query(None,ge=1),
    page_size: int = Query(None,ge=1)):
  
    if not page:
        page=1

    if not page_size:
        page_size=100

    try:
        users = session.query(User).options(defer(User.password)).order_by(
            desc(User.created_at)).limit(page_size).offset((page-1)*page_size).all()
        
        return {"msg": "users retrieved successfully","users":users}

    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))


@router.get('/{id}')
async def get_user_by_id(id:int ,current_user: str = Depends(get_current_user)):
    
    user = session.query(User).options(defer(User.password)).filter(User.id == id).first()
    
    if user:
        return {"msg": "User retrieved successfully", "user": user}
    else:
        raise HTTPException(status_code=404, detail="User not found")