from fastapi import APIRouter, Depends, HTTPException, Query, Body
from Oauth import get_current_user
from models.company import Contact
from config.db import Database,get_db
from sqlalchemy import desc
from datetime import datetime
from schemas.contact import ContactBaseSchema
from sqlalchemy.orm import Session



router = APIRouter(
    prefix="/contact",
    tags=["Contact"],
    responses={404: {"description": "Not found"}},
)


@router.post('/add')
async def create_contact(contact: ContactBaseSchema, db: Session = Depends(get_db),current_user: str = Depends(get_current_user),):
 
    try:
        contact.email = contact.email.lower()
        contact.created_at = datetime.utcnow()
        new_contact = Contact(**contact.model_dump())

        db.add(new_contact)
        db.commit()
        db.refresh(new_contact,attribute_names=['id'])

        return {"msg": "Contact registered successfully", "contact_id": new_contact.id}

    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()
 
    
    


@router.get("")
def get_contacts_for_id_or_company_id(id: int = Query(None),company_id: int = Query(None),db: Session = Depends(get_db)):
    try:
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
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()



@router.get('/all')
async def get_all_contacts(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
    page: int = Query(1,ge=1),
    page_size: int = Query(100,ge=1)):
  

    try:
        contacts = db.query(Contact).order_by(
            desc(Contact.id)).limit(page_size).offset((page-1)*page_size).all()
        
        return {"msg": "contacts retrieved successfully","contacts":contacts}
    
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()

    
    
@router.delete('')
async def delete_contact_by_id(id:int ,current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    try:
        contact = db.query(Contact).filter(Contact.id == id).first()
        if not contact:
            raise HTTPException(status_code=404, detail=f'No contact with this id: {id} found')
        
        if contact:
            db.delete(contact)
            db.query(Contact).filter(Contact.id > id).update({Contact.id: Contact.id - 1})
            db.commit()
            db.close()
            return {"msg": f"Contact id : {id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="contact not found")
        
    except HTTPException as http_exception:
        raise http_exception
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        db.close()
    

@router.put('/{contact_id}')
def update_contact(
    contact_id: int,
    contact_data: ContactBaseSchema,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()

        if not contact:
            raise HTTPException(status_code=404, detail=f'No contact with this id: {contact_id} found')

        for field, value in contact_data.model_dump(exclude_unset=True).items():
            setattr(contact, field, value)

        db.commit()

        return {"msg": "Contact updated successfully"}

    except HTTPException as http_exception:
        raise http_exception

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()


