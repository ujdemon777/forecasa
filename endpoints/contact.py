from fastapi import APIRouter, Depends, HTTPException, Query, Body
from Oauth import get_current_user
from models.company import Contact
from config.db import Database
from sqlalchemy import desc
from datetime import datetime
from schemas.contact import ContactBaseSchema



router = APIRouter(
    prefix="/contact",
    tags=["Contact"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)

@router.post('/add')
async def create_contact(contact: ContactBaseSchema):
 
    # new_contact = session.query(Contact).filter(Contact.company_id == contact.company_id).first()
    # print(new_contact)
    # if new_contact:
    #     raise HTTPException(status_code=409,
    #                         detail='Contact already exist')
    # ct = Contact()
    try:
        contact.email = contact.email.lower()
        contact.created_at = datetime.utcnow()
        new_contact = Contact(**contact.model_dump())

        session.add(new_contact)
        # session.refresh(ct, attribute_names=['id'])
        session.commit()
        session.refresh(new_contact)

        return {"msg": "Contact registered successfully", "contact_id": new_contact.id}

    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))
    
    


@router.get("")
def get_contacts_for_id_or_company_id(id: int = Query(None),company_id: int = Query(None)):
    if id:
        contact= session.query(Contact).filter(Contact.id == id).first()
    elif company_id:
        contact= session.query(Contact).filter(Contact.company_id == company_id).all()
    else:
        raise HTTPException(status_code=400, detail="provide id or company_id")


    if contact is None:
        raise HTTPException(status_code=404, detail="no contact found for this id")
    return {"msg": "contact retrieved successfully","contact":contact}



@router.get('/all')
async def get_all_contacts(
    current_user: str = Depends(get_current_user),
    page: int = Query(None,ge=1),
    page_size: int = Query(None,ge=1)):
  
    if not page:
        page=1

    if not page_size:
        page_size=100

    try:
        contacts = session.query(Contact).all()
        
        return {"msg": "contacts retrieved successfully","contacts":contacts}

    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
    
    
@router.delete('')
async def delete_contact_by_id(id:int ,current_user: str = Depends(get_current_user)):
    
    contact_query = session.query(Contact).filter(Contact.id == id)
    contact = contact_query.first()
    if not contact:
        return {"msg": "no contact found for this id"}
    
    if contact:
        contact_query.delete(synchronize_session=False)
        session.refresh(Contact(), attribute_names=['id'])
        session.commit()
        session.close()
        return {"msg": "Contact deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="contact not found")
    

@router.put('/{contact_id}')
def update_contact(
    contact_id: int,
    contact_data: ContactBaseSchema,
    current_user: str = Depends(get_current_user)
):
    try:
        contact= session.query(Contact).filter(Contact.id == contact_id)

        if not contact:
            raise HTTPException(status_code=404, detail=f'No contact with this id: {contact_id} found')

        contact.update(contact_data.model_dump(exclude_unset=True), synchronize_session=False)
        session.commit()

        return {"msg": "Contact updated successfully"}

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))


