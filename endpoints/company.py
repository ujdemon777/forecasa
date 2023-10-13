from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.response import Response
from models.model import Company
from config.db import Database
import json


router = APIRouter(
    prefix="/company",
    tags=["Company"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    correct_username = "ujjwal77"
    correct_password = "admin77"

    if credentials.username != correct_username or credentials.password != correct_password :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@router.get("/read")
async def read_forecasa_data(username = Depends(authenticate_user)):
    session = database.get_db_session(engine)
    data = session.query(Company).all()
    return Response(data, 200, "data retrieved successfully.", False)


@router.post("/add", response_description="forecasa data added into the database")
async def add_forecasa_data(request: Request, username = Depends(authenticate_user)):
 
    data = await request.body()
    data = data.decode('utf-8')
    data = json.loads(data)

    companies=data['companies']
    for cmp in companies:
        company= Company()
        # company.company_id = cmp['company_id']
        company.name= cmp['name'] or None
        company.dba = cmp['dba'] or None
        company.tags = cmp['tags'] or None
        company.leads =cmp['leads'] or None
        company.assignment_of_mortgage_transactions = cmp['assignment_of_mortgage_transactions'] or None
        company.deed_transactions = cmp['deed_transactions'] or None
        company.last_lender_used = cmp['last_lender_used'] or None
        company.other_lenders_used = cmp['other_lenders_used'] or None
        company.last_mortgage_date = cmp['last_mortgage_date'] or None
        company.last_transaction_date = cmp['last_transaction_date'] or None
        company.mortgage_transactions = cmp['mortgage_transactions'] or None
        company.party_count = cmp['party_count'] or None
        company.satisfaction_of_mortgage_transactions = cmp['satisfaction_of_mortgage_transactions'] or None
        company.transactions_as_borrower = cmp['transactions_as_borrower'] or None
        company.transactions_as_buyer = cmp['transactions_as_buyer'] or None
        company.transactions_as_lender = cmp['transactions_as_lender'] or None
        company.transactions_as_seller = cmp['transactions_as_seller'] or None
        company.last_county = cmp['last_county'] or None
        company.principal_address = cmp['principal_address'] or None
        company.principal_name = cmp['principal_name'] or None
        company.average_mortgage_amount = cmp['average_mortgage_amount'] or None
    
        session = database.get_db_session(engine)
        session.add(company)
        session.flush()
        # get id of the inserted product
        session.refresh(company, attribute_names=['id'])
        data = {"data": company.id}
        session.commit()
        session.close()
    return Response(data, 200, "forecasa data added successfully.", False)