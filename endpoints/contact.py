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
    
    try:
        contact.email = contact.email.lower()
        contact.created_at = datetime.utcnow()
        new_contact = Contact(**contact.model_dump())

        session.add(new_contact)
        session.commit()
        session.refresh(new_contact)

        return {"msg": "Contact registered successfully", "contact_id": new_contact.id}

    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))
    
    
@router.get("/test")
def get_contacts_for_company_id(company_id: int):
    contacts= session.query(Contact).filter(Contact.company_id == company_id).all()
    if contacts is None:
        raise HTTPException(status_code=404, detail="company not found")
    return contacts




# @router.get('/contacts')
# async def get_all_contacts(
#     current_user: str = Depends(get_current_user),
#     page: int = Query(None,ge=1),
#     page_size: int = Query(None,ge=1)):
  
#     if not page:
#         page=1

#     if not page_size:
#         page_size=100

#     try:
#         contacts = session.query(Contact).order_by(
#             desc(Contact.created_at)).limit(page_size).offset((page-1)*page_size).all()
        
#         return {"msg": "contacts retrieved successfully","users":contacts}

#     except Exception as e:
#         raise HTTPException(status_code=400,detail=str(e))
    

    
# @router.put('/contacts')
# async def get_all_contacts(contact: ContactBaseSchema,
#     current_user: str = Depends(get_current_user),
#     payload: dict = Body(None, description=""),
#     page: int = Query(None,ge=1),
#     page_size: int = Query(None,ge=1)):
  
#     if not page:
#         page=1

#     if not page_size:
#         page_size=100

#     try:
#         contact_query = session.query(Contact).filter(Contact.company_id == payload.company_id).first()

#         if not contact_query:
#             raise HTTPException(status_code=200,
#                             detail=f'No contact with this id: {payload.company_id} found')
        
#         contact.first_name = payload.first_name
        
#         contact.update(post.dict(exclude_unset=True), synchronize_session=False)
        
#         return {"msg": "contacts retrieved successfully","users":contact}

#     except Exception as e:
#         raise HTTPException(status_code=400,detail=str(e))


# @router.get('/{id}')
# async def get_user_by_id(id:int ,current_user: str = Depends(get_current_user)):
    
#     contact = session.query(Contact).filter(Contact.id == id).first()
    
#     if contact:
#         return {"msg": "User retrieved successfully", "user": contact}
#     else:
#         raise HTTPException(status_code=404, detail="User not found")