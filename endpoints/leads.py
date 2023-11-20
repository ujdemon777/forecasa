from fastapi import APIRouter, Depends, HTTPException, Query, Body,File, UploadFile
from models.company import Company
from config.db import Database
from datetime import datetime
from sqlalchemy import and_, or_, func
from dotenv import load_dotenv, find_dotenv
from utils import authenticate_user
from utils import upload_file
from fastapi.responses import JSONResponse
from Oauth import get_current_user
from sqlalchemy import desc



_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/leads",
    tags=["Leads"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)



@router.get("/read")
async def get_leads(current_user: str = Depends(get_current_user),
        page: int = Query(None,ge=1),
        page_size: int = Query(None,ge=1)
    ):

    if not page:
        page=1

    if not page_size:
        page_size=100

    leads = session.query(Company).order_by(
                    desc(Company.created_at)).limit(page_size).offset((page-1)*page_size).all()
    return JSONResponse({"leads" : leads, "msg":"All leads retrieved successfully"})




@router.post("/filter")
async def filter_leads(current_user: str = Depends(get_current_user),
        mortgage_transactions: dict = Body(None, description="Minimum & Maximum value of the range"),
        last_mortgage_date: dict = Body(None, description="Start date & End date of the range"),
        last_transaction_date: dict = Body(None, description="Start date & End date of the range (YYYY-MM-DD)"),
        average_mortgage_amount: dict = Body(None, description="Minimum & Maximum value of the range"),
        last_lender_used: list = Query(None, description="List of categories to filter"),
        page: int = Query(None,ge=1),
        page_size: int = Query(None,ge=1)
    ):

    if not page:
        page=1

    if not page_size:
        page_size=100
    

    try:
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
            leads = session.query(Company).filter(and_(*filters)).order_by(
                    desc(Company.created_at)).limit(page_size).offset((page-1)*page_size).all()
            return JSONResponse({"leads":leads, "msg":"leads generated"})

        else:
            return JSONResponse({"msg":"No Filters Provided"})

    except Exception as e:
        raise HTTPException(status_code=400,detail=f"error occurred while fetching leads data:{str(e)}")



@router.post("/add")
async def add_leads(file: UploadFile = File(...),current_user: str = Depends(get_current_user)):

    """
    Adding leads Company Data to the Database

    This endpoint allows you to add leads data to the database. It expects a JSON request containing a list of companies
    The companies are added to the database, and a list of added company IDs is returned upon successful insertion.

    Parameters:
        - `request`: FastAPI Request object.
        - `username`: User authentication dependency.

    Request Format:
    {
        "companies": [
            {
                "id": 123,
                "name": "Company Name",
                ...
            },
            ...
        ]
    }

    Response:
    - If successful, returns a list of added company IDs.
    - If no companies are provided in the request, returns an error response.
    - In case of an integrity error, returns an error response with a 400 status code.

    """

    try:
        response = await upload_file(file)
        if response.get("status_code") == 200:
            companies=response.get('data' , dict()).get("companies",[])

        if not companies:
            raise JSONResponse({"msg":"No Companies Provided in request"})


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

        return JSONResponse({"companies_id":added_company_ids, "msg":"leads data added successfully"})
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400,detail=f"Integrity error occurred while adding leads data:{str(e)}")




@router.get("/value")
async def get_min_max_txn(username = Depends(authenticate_user)):
    
    min_mortgage = session.query(func.min(Company.mortgage_transactions)).scalar()
    max_mortgage = session.query(func.max(Company.mortgage_transactions)).scalar()

    min_avg_mortgage_amount = session.query(func.min(Company.average_mortgage_amount)).scalar()
    max_avg_mortgage_amount = session.query(func.max(Company.average_mortgage_amount)).scalar()

    data={'min_mortgage':min_mortgage,'max_mortgage':max_mortgage,'min_avg_mortgage_amount':min_avg_mortgage_amount, 'max_avg_mortgage_amount':max_avg_mortgage_amount}
    return JSONResponse({"data": data, "msg":"mortage data retrieved successfully"})










