from fastapi import APIRouter, Depends, HTTPException, Query
from Oauth import get_current_user
from models.business import Business
from models.company import Company, Contact
from models.user import User
from config.db import get_db
from sqlalchemy.orm import defer,Session
from sqlalchemy import desc
from schemas.user import UserUpdateSchema



router = APIRouter(
    prefix="/demo",
    tags=["Demo"],
    responses={404: {"description": "Not found"}},
)



@router.get('/demo')              
async def get_all_users(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1),
    model:str = Query(...),
    id:int = Query(None),
    company_id : int = Query(None)
    ):

    try:
        if model=='User' :
            if not id:
                users = db.query(User).options(defer(User.password)).order_by(
                    desc(User.id)).limit(page_size).offset((page-1)*page_size).all()
                
                return {"msg": "users retrieved successfully","users":users}
            
            else:
                user = db.query(User).options(defer(User.password)).filter(User.id == id).first()
                if user:
                    return {"msg": "User retrieved successfully", "user": user}
                else:
                    raise HTTPException(status_code=404, detail="User not found")

        elif model=='Company':
            if not id:
                leads = db.query(Company).order_by(
                                desc(Company.id)).limit(page_size).offset((page-1)*page_size).all()
                return {"leads" : leads, "msg":"All leads retrieved successfully"}
            else:
                lead = db.query(Company).filter(Company.id == id).first()
        
                if lead:
                    return {"msg": "Lead retrieved successfully", "lead": lead}
                else:
                    raise HTTPException(status_code=404, detail="Lead not found")
        

        elif model == 'Business':
            if not id:
                business = db.query(Business).options(defer(Business.api_key),defer(Business.fernet_key)).order_by(
                    desc(Business.id)).limit(page_size).offset((page-1)*page_size).all()
                
                return {"msg": "business retrieved successfully","business":business}
            else:
                business = db.query(Business).options(defer(Business.api_key),defer(Business.fernet_key)).filter(Business.business_id == id).order_by(
            desc(Business.id)).limit(page_size).offset((page-1)*page_size).all()
        
                return {"msg": "business retrieved successfully","business":business}

        elif model == 'Contact':
            if not id:
                contacts = db.query(Contact).order_by(
                    desc(Contact.id)).limit(page_size).offset((page-1)*page_size).all()
                
                return {"msg": "contacts retrieved successfully","contacts":contacts}
            else:
                if id:
                    contact= db.query(Contact).filter(Contact.id == id).first()
                elif company_id:
                    contact= db.query(Contact).filter(Contact.company_id == company_id).all()
                else:
                    raise HTTPException(status_code=400, detail="provide id or company_id")

                if contact is None:
                    raise HTTPException(status_code=404, detail="no contact found for this id")
                
                return {"msg": "contact retrieved successfully","contact":contact}

    except HTTPException as http_exception:
        raise http_exception
            
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
    finally:
        db.close()