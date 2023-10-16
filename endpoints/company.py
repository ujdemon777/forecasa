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
        company.name= cmp.get('name')
        company.dba = cmp.get('dba')
        company.tags = cmp.get('tags')
        company.leads =cmp.get('leads')
        company.assignment_of_mortgage_transactions = cmp.get('assignment_of_mortgage_transactions')
        company.deed_transactions = cmp.get('deed_transactions')
        company.last_lender_used = cmp.get('last_lender_used')
        company.other_lenders_used = cmp.get('other_lenders_used')
        company.last_mortgage_date = cmp.get('last_mortgage_date')
        company.last_transaction_date = cmp.get('last_transaction_date')
        company.mortgage_transactions = cmp.get('mortgage_transactions')
        company.party_count = cmp.get('party_count')
        company.satisfaction_of_mortgage_transactions = cmp.get('satisfaction_of_mortgage_transactions')
        company.transactions_as_borrower = cmp.get('transactions_as_borrower')
        company.transactions_as_buyer = cmp.get('transactions_as_buyer')
        company.transactions_as_lender = cmp.get('transactions_as_lender')
        company.transactions_as_seller = cmp.get('transactions_as_seller')
        company.last_county = cmp.get('last_county')
        company.principal_address = cmp.get('principal_address')
        company.principal_name = cmp.get('principal_name')
        company.average_mortgage_amount = cmp.get('average_mortgage_amount')
    
        session = database.get_db_session(engine)
        session.add(company)
        session.flush()
        # get id of the inserted product
        session.refresh(company, attribute_names=['id'])
        data = {"data": company.id}
        session.commit()
        session.close()
    return Response(data, 200, "forecasa data added successfully.", False)