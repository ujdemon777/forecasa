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
import requests

_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/cw_filters",
    tags=["Filters"],
    responses={404: {"description": "Not found"}},
)

@router.get("/value")
async def get_min_max_txn(blob_name: str = Query(..., description="name of particular blob")):

    query_parameters = {
        "blob_name":blob_name
    }
    response = requests.get("http://127.0.0.1:8000/cw/blob",params=query_parameters)
    print(response)
    companies = response["data"]["companies"]
    a=min(company["mortgage_transactions"] for company in companies)
   
    return Response(a, "data retrieved successfully." , 200 , False)