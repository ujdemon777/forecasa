from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from models.transaction import Transaction
from config.db import Database
import json
from utils import authenticate_user


router = APIRouter(
    prefix="",
    tags=["Transaction"],
    responses={404: {"description": "Not found"}},
)

database = Database()
engine = database.get_db_connection()
session = database.get_db_session(engine)


@router.get("/read")
async def read_forecasa_data(username = Depends(authenticate_user)):
    
    data = session.query(Transaction).all()
    return {"msg":"data retrieved successfully."}


@router.post("/add", response_description="forecasa data added into the database")
async def add_forecasa_data(request: Request, username = Depends(authenticate_user)):
 
    forecasa_data = await request.body()
    forecasa_data = forecasa_data.decode('utf-8')
    forecasa_data = json.loads(forecasa_data)

    transactions=forecasa_data['transactions']
    for txn in transactions:
        transaction = Transaction()
        transaction.fc_transaction_id= txn['fc_transaction_id']
        transaction.fc_house_id = txn['fc_house_id']
        transaction.grantor = txn['grantor']
        transaction.grantee = txn['grantee']
        transaction.party_company = txn['party_company']
        transaction.cross_party_company = txn['cross_party_company']
        transaction.county = txn['county']
        transaction.fc_created_at = txn['fc_created_at']
        transaction.fc_updated_at = txn['fc_updated_at']
        transaction.mortgage_maturity_date = txn['mortgage_maturity_date']
        transaction.pdf_id = txn['pdf_id']
        transaction.recorded_date = txn['recorded_date']
        transaction.signer = txn['signer']
        transaction.transaction_date = txn['transaction_date']
        transaction.transaction_number = txn['transaction_number']
        transaction.transaction_type = txn['transaction_type']
        transaction.lat = txn['lat']
        transaction.lng = txn['lng']
        transaction.fc_10_yr_t_note = txn['fc_10_yr_t_note']
        transaction.transaction_meta = txn['transaction_meta']
        transaction.amount = txn['amount']
        transaction.address = txn['address']
        transaction.pdf = txn['pdf']
        transaction.fc_party_company = txn['fc_party_company']
        transaction.fc_cross_party_company = txn['fc_cross_party_company']
        transaction.state_name = txn['state_name']
        transaction.msa_name = txn['msa_name']
        transaction.fip_code = txn['fip_code']

        session = database.get_db_session(engine)
        session.add(transaction)
        session.flush()
        session.refresh(transaction, attribute_names=['id'])
        data = {"transaction": transaction.id}
        session.commit()
        session.close()
    return {"msg": "transaction data added successfully"}