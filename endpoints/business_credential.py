from fastapi import APIRouter, Depends, HTTPException, Query, Body
from Oauth import get_current_user
from models.business import Business
from config.db import Database,get_db
from sqlalchemy import desc
from datetime import datetime
from schemas.business import BusinessBaseSchema, UpdateBusinessBaseSchema
from sqlalchemy.orm import Session,defer
from utils import encrypt_password



router = APIRouter(
    prefix="/business",
    tags=["Business"],
    responses={404: {"description": "Not found"}},
)


@router.post('/add')
async def create_credential(business: BusinessBaseSchema, db: Session = Depends(get_db),current_user: str = Depends(get_current_user)):
 
    try:
        business_source = db.query(Business.source).filter(Business.business_id == business.business_id).all()

        for business_src in business_source:
            business_src = business_src[0]
            if business.source == business_src:
                raise HTTPException(status_code=409, detail="Business with this source already exist")

        business.created_at = datetime.utcnow()
        business.updated_at = datetime.utcnow()

        encrypt_api_key , fernet_key = await encrypt_password(business.api_key)
        print(f"encrypt_api_key:{encrypt_api_key},fernet_key:{fernet_key}")
        business.api_key = encrypt_api_key
        business.fernet_key = fernet_key

        new_business = Business(**business.model_dump())

        db.add(new_business)
        db.commit()
        db.refresh(new_business,attribute_names=['id'])

        return {"msg": "new_business registered successfully", "business_id": new_business.business_id}

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()
 

@router.get('/all')
async def get_all_business(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1)):
  

    try:
        business = db.query(Business).options(defer(Business.api_key),defer(Business.fernet_key)).order_by(
            desc(Business.id)).limit(page_size).offset((page-1)*page_size).all()
        
        return {"msg": "business retrieved successfully","business":business}
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()



@router.get('/{business_id}')
async def get_business_by_id(
    business_id:int ,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1)):
  

    try:
        business = db.query(Business).options(defer(Business.api_key),defer(Business.fernet_key)).filter(Business.business_id == business_id).order_by(
            desc(Business.id)).limit(page_size).offset((page-1)*page_size).all()
        
        return {"msg": "business retrieved successfully","business":business}
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()
   

@router.put('/{business_id}')
async def update_business(
    business_id: int,
    business_data: UpdateBusinessBaseSchema,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        business = db.query(Business).filter(Business.business_id == business_id).all()

        if not business:
            raise HTTPException(status_code=404, detail=f'No business with this id: {business_id} found')
        


        if business_data.api_key:
            encrypt_api_key , fernet_key = await encrypt_password(business_data.api_key)
            business.api_key = encrypt_api_key
            business.fernet_key = fernet_key

        if business_data.source:
            business.source = business_data.source
        

        db.commit()

        return {"msg": "Business updated successfully"}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


