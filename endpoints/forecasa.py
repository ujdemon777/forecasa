from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.response import Response
from models.model import Forecasa
from config.db import Database
import json
# from endpoints.transaction import forecasa_data


router = APIRouter(
    prefix="",
    tags=["Forecasa"],
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
    data = session.query(Forecasa).all()
    return Response(data, 200, "data retrieved successfully.", False)


@router.post("/add", response_description="forecasa data added into the database")
async def add_forecasa_data(request: Request, username = Depends(authenticate_user)):
 
    forecasa_data = await request.body()
    forecasa_data = forecasa_data.decode('utf-8')
    forecasa_data = json.loads(forecasa_data)

    transactions=forecasa_data['transactions']
    for txn in transactions:
        forecasa = Forecasa()
        forecasa.fc_transaction_id= txn['fc_transaction_id']
        forecasa.fc_house_id = txn['fc_house_id']
        forecasa.grantor = txn['grantor']
        forecasa.grantee = txn['grantee']
        forecasa.party_company = txn['party_company']
        forecasa.cross_party_company = txn['cross_party_company']
        forecasa.county = txn['county']
        forecasa.fc_created_at = txn['fc_created_at']
        forecasa.fc_updated_at = txn['fc_updated_at']
        forecasa.mortgage_maturity_date = txn['mortgage_maturity_date']
        forecasa.pdf_id = txn['pdf_id']
        forecasa.recorded_date = txn['recorded_date']
        forecasa.signer = txn['signer']
        forecasa.transaction_date = txn['transaction_date']
        forecasa.transaction_number = txn['transaction_number']
        forecasa.transaction_type = txn['transaction_type']
        forecasa.lat = txn['lat']
        forecasa.lng = txn['lng']
        forecasa.fc_10_yr_t_note = txn['fc_10_yr_t_note']
        forecasa.transaction_meta = txn['transaction_meta']
        forecasa.amount = txn['amount']
        forecasa.address = txn['address']
        forecasa.pdf = txn['pdf']
        forecasa.fc_party_company = txn['fc_party_company']
        forecasa.fc_cross_party_company = txn['fc_cross_party_company']
        forecasa.state_name = txn['state_name']
        forecasa.msa_name = txn['msa_name']
        forecasa.fip_code = txn['fip_code']

        session = database.get_db_session(engine)
        session.add(forecasa)
        session.flush()
        # get id of the inserted product
        session.refresh(forecasa, attribute_names=['id'])
        data = {"forecasa": forecasa.id}
        session.commit()
        session.close()
    return Response(transactions, 200, "forecasa data added successfully.", False, "bronze")