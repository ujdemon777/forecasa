from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.response import Response,ErrorResponse
from models.model import Company
from config.db import Database
import json
from datetime import datetime
from sqlalchemy import and_,or_


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
    return Response(data, "data retrieved successfully." , 200 , False)

@router.get("/filter")
async def filter_data(
    mortgage_transactions: dict = Body(None, description="Minimum value of the range"),
    last_mortgage_date: dict = Body(None, description="Maximum value of the range"),
    last_transaction_date: dict = Body(None, description="Start date of the range (YYYY-MM-DD)"),
    average_mortgage_amount: dict = Body(None, description="End date of the range (YYYY-MM-DD)"),
    last_lender_used: list = Query(None, description="List of categories to filter")
    ):
    
    session = database.get_db_session(engine)


    filters = []
    if mortgage_transactions and isinstance(mortgage_transactions, dict):
        min_value = mortgage_transactions.get('min_value')
        max_value = mortgage_transactions.get('max_value')
        if min_value:
            filters.append(Company.mortgage_transactions >= min_value)
        if max_value:
            filters.append(Company.mortgage_transactions <= max_value)


    if last_mortgage_date and isinstance(last_mortgage_date, dict):
        start_date = last_mortgage_date.get('start_date')
        end_date = last_mortgage_date.get('end_date')
        if start_date:
            filters.append(Company.last_mortgage_date >= start_date)
        if end_date:
            filters.append(Company.last_mortgage_date <= end_date)

    if average_mortgage_amount and isinstance(average_mortgage_amount, dict):
        min_value = average_mortgage_amount.get('min_value')
        max_value = average_mortgage_amount.get('max_value')
        if min_value:
            filters.append(Company.average_mortgage_amount >= min_value)
        if max_value:
            filters.append(Company.average_mortgage_amount <= max_value)


    if last_transaction_date and isinstance(last_transaction_date, dict):
        start_date = last_transaction_date.get('start_date')
        end_date = last_transaction_date.get('end_date')
        if start_date:
            filters.append(Company.last_transaction_date >= start_date)
        if end_date:
            filters.append(Company.last_transaction_date <= end_date)

    if last_lender_used:
        category_filters = [Company.last_lender_used == last_lender_used for last_lender_used in last_lender_used]
        filters.append(or_(*category_filters))


    if filters:
        data = session.query(Company).filter(and_(*filters)).all()
        print(len(data))
        return Response(data, "data retrieved successfully." , 200 , False)
    else:
        return ErrorResponse("No companies provided in the request", 400 , False)

    



@router.post("/add", response_description="forecasa data added into the database")
async def add_forecasa_data(request: Request, username = Depends(authenticate_user)):

    try:
        data = await request.json()

        companies=data.get('companies' , dict())

        if not companies:
            return ErrorResponse("No companies provided in the request", 400 , False)

        session = database.get_db_session(engine)

        added_company_ids = []

        for cmp in companies:
            print(f"debug{cmp.get('id')}")
            company= Company()
            company.company_id = cmp.get('id')
            company.name= cmp.get('name')
            company.dba = cmp.get('dba')
            company.tag_names = cmp.get('tag_names')
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
            company.created_at = datetime.utcnow()
            company.updated_at = datetime.utcnow()

        
            
            session.add(company)
            session.flush()
            added_company_ids.append(cmp.get('id'))
            # get id of the inserted product
            # session.refresh(company, attribute_names=['id'])
            # data = {"data": company.id}
        session.commit()
        session.close()

        return Response(added_company_ids, "forecasa data added successfully", 200, False)
        
    except Exception as e:
        session.rollback()
        return ErrorResponse("Integrity error occurred while adding forecasa data", 500, str(e))
