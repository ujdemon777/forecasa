from fastapi import APIRouter, Depends, HTTPException, Query
from Oauth import get_current_user
from models.user import User
from config.db import get_db
from sqlalchemy.orm import defer,Session
from sqlalchemy import desc
from schemas.user import UserUpdateSchema



router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)



@router.get('/all')              
async def get_all_users(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1)):
  

    try:
        users = db.query(User).options(defer(User.password)).order_by(
            desc(User.id)).limit(page_size).offset((page-1)*page_size).all()
        
        return {"msg": "users retrieved successfully","users":users}

    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    finally:
        db.close()


@router.get('/{id}')
async def get_user_by_id(id:int ,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    
    try:
        user = db.query(User).options(defer(User.password)).filter(User.id == id).first()
        
        if user:
            return {"msg": "User retrieved successfully", "user": user}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()


@router.put('/{id}')
async def update_user_by_id(id:int ,user_data: UserUpdateSchema ,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    
    try:
        user = db.query(User).filter(User.id == id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f'No user with this id: {id} found')
    
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        db.commit()

        return {"msg": "User updated successfully"}
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()


