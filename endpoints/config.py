from fastapi import APIRouter, Depends, HTTPException, Query, Body
from Oauth import get_current_user
from models.user import Blob
from config.db import get_db
from sqlalchemy.orm import defer,Session
from sqlalchemy import desc , and_

from models.user import User




router = APIRouter(
    prefix="/config",
    tags=["Config"],
    responses={404: {"description": "Not found"}},
)



@router.post('/all')              
async def get_all_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    experiment: int = Body(None, description="name of file"),
    status: str = Body(None, description="Bronze/Silver/Gold"),
    createdAt: dict = Body(None, description="Start date & End date of the range (YYYY-MM-DD)"),
    user: int = Body(None, description="user_id"),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1)):
  

    try:
        filters = []

        if createdAt and isinstance(createdAt, dict):
            start_date = createdAt.get('start_date')
            end_date = createdAt.get('end_date')
            if start_date:
                filters.append(Blob.created_at >= start_date)
            if end_date:
                filters.append(Blob.created_at <= end_date)

        if status and isinstance(status, str):
            filters.append(Blob.status == status)

        if experiment and isinstance(experiment, int):
            filters.append(Blob.id == experiment)

        if user and isinstance(user, int):
            filters.append(Blob.user_id == user)
            # user_id = db.query(User.id).filter(User.name == user_name).first()
            # print(user_id)
            # if user_id is not None:
            #     user_id = user_id[0]
            #     filters.append(Blob.user_id == user_id)
            # else:
            #     filters.append(Blob.user_id == user_id)


        if filters:
            configs = db.query(Blob,User.name).join(User,Blob.user_id==User.id).filter(and_(*filters)).order_by(
                    desc(Blob.id)).limit(page_size).offset((page-1)*page_size).all()
            
            result_configs = []
            
            for blob, user_name in configs:
                blob.user_name = user_name
                result_configs.append(blob)
            return {"msg": "configs retrieved successfully","configs":result_configs}
        
        else:
            configs = db.query(Blob,User.name).join(User,Blob.user_id==User.id).order_by(
                desc(Blob.id)).limit(page_size).offset((page-1)*page_size).all()

            result_configs = []
            
            for blob, user_name in configs:
                # a=(blob.__dict__['user_name']= user_name)
                blob.user_name = user_name
                result_configs.append(blob)

            # result_configs = [blob._asdict() | {'user_name': user_name} for blob, user_name in configs]
            return {"msg": "All configs retrieved successfully","configs":result_configs}

    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    finally:
        db.close()


@router.get('/{id}')
async def get_user_by_id(id:int ,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    
    try:
        config = db.query(Blob).filter(Blob.id == id).first()
        
        if config:
            return {"msg": "config retrieved successfully", "config": config}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()