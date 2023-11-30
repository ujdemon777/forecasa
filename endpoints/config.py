from fastapi import APIRouter, Depends, HTTPException, Query
from Oauth import get_current_user
from models.blobs import Blob
from config.db import get_db
from sqlalchemy.orm import defer,Session
from sqlalchemy import desc



router = APIRouter(
    prefix="/config",
    tags=["Config"],
    responses={404: {"description": "Not found"}},
)



@router.get('/all')              
async def get_all_users(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1)):
  

    try:
        configs = db.query(Blob).order_by(
            desc(Blob.id)).limit(page_size).offset((page-1)*page_size).all()
        
        return {"msg": "configs retrieved successfully","configs":configs}

    
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