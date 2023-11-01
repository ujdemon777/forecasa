from tkinter.tix import ComboBox
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.response import Response,ErrorResponse
from models.model import Company
from config.db import Database
import json
from datetime import datetime
from sqlalchemy import and_, or_, func
from dotenv import load_dotenv, find_dotenv
import os
import httpx

from azure.storage.filedatalake import  DataLakeDirectoryClient, DataLakeServiceClient
from azure.storage.blob import BlobServiceClient
import base64
from io import BufferedReader
from azure.storage.blob import BlobClient




_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/company",
    tags=["Company"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()



azure_storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
azure_storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
azure_storage_file_system = os.getenv("AZURE_STORAGE_FILE_SYSTEM")

# Initialize ADLS client
adls_client = DataLakeServiceClient(account_url=f"https://{azure_storage_account_name}.dfs.core.windows.net", credential=azure_storage_account_key)


# adls_client = DataLakeServiceClient(account_url=azure_storage_account_name, credential=azure_storage_account_key)

print(adls_client)


def authenticate_user(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """
    Authenticate User with Basic Authentication

    This function is used for authenticating a user with Basic Authentication. It checks the provided HTTPBasicCredentials
    against the stored username and password. If the credentials are valid, the function returns the authenticated username.

    Parameters:
        - `credentials`: HTTPBasicCredentials - The provided username and password for authentication.

    Returns:
        - If authentication is successful, returns the authenticated username.
        - If the provided credentials are invalid, raises an HTTPException with a 401 Unauthorized status.
    """

    username = os.getenv("username")
    password = os.getenv("password")

    if credentials.username != username or credentials.password != password :
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




@router.post("/filter")
async def filter_data(username = Depends(authenticate_user),
    mortgage_transactions: dict = Body(None, description="Minimum value of the range"),
    last_mortgage_date: dict = Body(None, description="Maximum value of the range"),
    last_transaction_date: dict = Body(None, description="Start date of the range (YYYY-MM-DD)"),
    average_mortgage_amount: dict = Body(None, description="End date of the range (YYYY-MM-DD)"),
    last_lender_used: list = Query(None, description="List of categories to filter")
    ):
    
    session = database.get_db_session(engine)

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
            data = session.query(Company).filter(and_(*filters)).all()
            print(len(data))
            return Response(data, "data retrieved successfully." , 200 , False)

        else:
            return ErrorResponse("No filters provided", 400 , False)

    except Exception as e:
        return ErrorResponse("error occurred while fetching forecasa data", 500, str(e))





    



@router.post("/add", response_description="forecasa data added into the database")
async def add_forecasa_data(request: Request, username = Depends(authenticate_user)):

    """
    Adding Forecasa Company Data to the Database

    This endpoint allows you to add Forecasa data to the database. It expects a JSON request containing a list of companies
    with their details. The companies are added to the database, and a list of added company IDs is returned upon successful insertion.

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
    - In case of an integrity error, returns an error response with a 500 status code.

    """

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




@router.get("/value")
async def get_min_max_txn(username = Depends(authenticate_user)):
    
    session = database.get_db_session(engine)
    min_mortgage = session.query(func.min(Company.mortgage_transactions)).scalar()
    max_mortgage = session.query(func.max(Company.mortgage_transactions)).scalar()

    min_avg_mortgage_amount = session.query(func.min(Company.average_mortgage_amount)).scalar()
    max_avg_mortgage_amount = session.query(func.max(Company.average_mortgage_amount)).scalar()

    data={'min_mortgage':min_mortgage,'max_mortgage':max_mortgage,'min_avg_mortgage_amount':min_avg_mortgage_amount, 'max_avg_mortgage_amount':max_avg_mortgage_amount}
    return Response(data, "data retrieved successfully." , 200 , False)



@router.get("/forecasa/states")
async def fetch_states():
    params = {"api_key": "JcGtDHRCa2p4IfOhs13veg"}  

    try:
        async with httpx.AsyncClient() as client:

            url = "https://webapp.forecasa.com/api/v1/geo/counties_by_states"  
            response = await client.get(url, params=params)


            if response.status_code == 200:  
                print("uk")
                data = response.json()
                return {"states": data}
            elif response.status_code == 429: 
                print("debug")
                cookie = response.headers.get("set-cookie")
                # res.set_cookie(key="forecasa", value=cookie)
                # print(res)

                cookies = {"forecasa": cookie}

               
                response1 = await client.get(url, cookies=cookies)
                data = response1.json()
                # print(data)
                return {"states": data}

    except Exception as error:
        return {"error": str(error)}



@router.post("/forecasa/fetch_company_data")
async def fetch_company_data(
    body = Body(None, description="List of categories to filter"),
    # company_name: string = Query(None, description="List of categories to filter"),
    # counties: list = Body(None, description="List of categories to filter")
):
    session = database.get_db_session(engine)
    # print(type(company_tags))
    print(f"dbody{body}")
    params={"q[tags_name_in][]":body.get('company_tags'),"[transactions][q][county_in][]":body.get('counties'),"q[name_cont]":body.get('company_name'),"api_key": "JcGtDHRCa2p4IfOhs13veg"}
   

    async with httpx.AsyncClient() as client:

        url = "https://webapp.forecasa.com/api/v1/companies"  
        response = await client.get(url, params=params)
        print(f"res1{response.url}")

        if response.status_code == 200:
            print("uk")
            try:
                data = response.json()
                return data
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail="Error parsing JSON data from the API")
            
        elif response.status_code == 429: 
                print("debug")
                cookie = response.headers.get("set-cookie")
                cookies = {"forecasa": cookie}

                params.pop('api_key')
                response1 = await client.get(url, cookies=cookies,params=params)
                print(f"res2{response1.url}")
                data = response1.json()
                # print(data)
                return {"states": data}







@router.get("/blob")
async def create_blob():
    try:
        container_name = "capitalpro"

        blob_name = "capital"

        sas_url="https://traningshorthills.blob.core.windows.net/capitalpro?sp=racwdli&st=2023-10-20T11:15:11Z&se=2024-10-19T19:15:11Z&sv=2022-11-02&sr=c&sig=a2T2F33PkVxswp9diZd16uRl23gionr%2BLn8OtI7eEvg%3D"

        blob_client = BlobClient.from_blob_url(sas_url)

        # blob_name = str(f'{uuid.uuid4()}.md')
        
        # Create a BlobServiceClient
        # blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=azure_storage_account_key)
        
        # # Get a reference to the container and blob
        # container_client = blob_service_client.get_container_client(container_name)
        # blob_client = container_client.get_blob_client(blob_name)

        # Create a local directory to hold blob data
        local_path = "./data"
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        else:
            print("Directory already exists.")


        # Create a file in the local data directory to upload and download
        local_file_name = str('ukkk') + ".txt"
        upload_file_path = os.path.join(local_path, local_file_name)

        # Write text to the file
        file = open(file=upload_file_path, mode='w')
        file.write("Hello, ujjwal!")
        file.close()

        # Create a blob client using the local file name as the name for the blob
        # blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

        print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

        # Upload the created file
        with open(file=upload_file_path, mode="rb") as data:
            f = data.read()
            # encoded_data = f.encode('utf-8')  # Encode the text as bytes
            # print(encoded_data)
            blob_client.upload_blob(f, blob_type="BlockBlob")

        # local_file_path = "/Users/shtlpmac042/desktop/uk.txt"

        # blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        # print(blob_client)

        # with open(local_file_path, 'r') as data:
        #     f = data.read()
        #     encoded_data = f.encode('utf-8')  # Encode the text as bytes
        #     print(encoded_data)
        #     blob_client.upload_blob(encoded_data, blob_type="BlockBlob")

        print("Blob created successfully.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")
    


@router.get("/blob")
async def read_blob():
    try:
        container_name = "capitalpro"

        # blob_name = "capitalpro"

        # blob_name = str(f'{uuid.uuid4()}.md')
        
        # Create a BlobServiceClient
        sas_url="sp=racwdli&st=2023-10-20T11:15:11Z&se=2024-10-19T19:15:11Z&sv=2022-11-02&sr=c&sig=a2T2F33PkVxswp9diZd16uRl23gionr%2BLn8OtI7eEvg%3D"

        blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=sas_url)
        
        # Get a reference to the container and blob
        container_client = blob_service_client.get_container_client(container_name)
        # blob_client = container_client.get_blob_client(blob_name)

        # container_client = blob_service_client.get_container_client(container_name)

        blob_list = container_client.list_blobs()
        print(blob_list)
        print(type(blob_list))
        print("debug1")
        blobs=[]
        for blob in blob_list:
            print(f"File Name: {blob.name}")
            blobs.append(f"File Name: {blob.name}")
        return Response(blobs, f"{len(blobs)} blobs retrieved successfully." , 200 , False)

        # # Download a file from the container
        # file_name = "your_file_name"
        # blob_client = container_client.get_blob_client(file_name)
        # with open(file_name, "wb") as file:
        #     file.write(blob_client.download_blob().readall())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")