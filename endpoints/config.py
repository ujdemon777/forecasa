from fastapi import APIRouter, Depends, HTTPException, Query, Body
from Oauth import get_current_user
from models.blobs import Blob
from config.db import get_db
from sqlalchemy.orm import defer,Session
from sqlalchemy import desc , and_




router = APIRouter(
    prefix="/config",
    tags=["Config"],
    responses={404: {"description": "Not found"}},
)



@router.post('/all')              
async def get_all_users(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    file_name: str = Body(None, description="name of file"),
    status: str = Body(None, description="Bronze/Silver/Gold"),
    createdAt: dict = Body(None, description="Start date & End date of the range (YYYY-MM-DD)"),
    user_id: int = Body(None, description="id"),
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

        if file_name and isinstance(file_name, str):
            filters.append(Blob.file_name == file_name)

        # if user_id and isinstance(user_id, int):
        #     filters.append(Blob.user_name == user_id)

        if filters:
            configs = db.query(Blob).filter(and_(*filters)).order_by(
                    desc(Blob.id)).limit(page_size).offset((page-1)*page_size).all()
            return {"msg": "configs retrieved successfully","configs":configs}
        
        else:
            configs = db.query(Blob).order_by(
                desc(Blob.id)).limit(page_size).offset((page-1)*page_size).all()
        
            return {"msg": "All configs retrieved successfully","configs":configs}

    
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