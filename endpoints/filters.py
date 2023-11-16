from tkinter.tix import ComboBox
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from models.response import Response,ErrorResponse
import json,os,httpx
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from utils import authenticate_user
from models.schema import CompanyFilters
import requests

_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/filters",
    tags=["Filters"],
    responses={404: {"description": "Not found"}},
)


forecasa_api_key= os.getenv("FORECASA_API_KEY")

@router.get("/read")
async def read_forecasa_data():
    data = {"a":"ujjwal"}
    return Response(data, "data retrieved successfully." , 200 , False)


@router.post("/filter")
async def fetch_company_data(filters: CompanyFilters):
    params = {
        "api_key": forecasa_api_key
    }

    if filters.page:
        params[f"page"] = filters.page

    if filters.page_size:
        params[f"page_size"] = filters.page_size

    if filters.transaction_tags:
        params[f"q[tags_name_in][]"] = filters.transaction_tags

    if filters.child_sponsor:
        params["q[name_cont]"] = filters.child_sponsor

    if filters.counties:
        params["q[transactions][q][county_in][]"] = filters.counties

    if filters.transaction_type:
        params[f"transactions][q][transaction_type_in][]"] = filters.transaction_type

    if filters.amount:
        if filters.amount.get("max_value"):
            params[f"transactions[q][amount_lteq]"] = filters.amount.get("max_value")
        if filters.amount.get("min_value"):
            params[f"transactions[q][amount_gteq]"] = filters.amount.get("min_value")
        
    try:
        async with httpx.AsyncClient() as client:

            url = "https://webapp.forecasa.com/api/v1/companies"  
            response = await client.get(url, params=params)

            if response.status_code == 200:  
                data = response.json()
                return {"companies": data.get("companies", []), "companies_total_count": data.get("companies_total_count", 0)}
            # elif response.status_code == 429: 
            #     print("debug")
            #     cookie = response.headers.get("set-cookie")
            #     cookies = {"forecasa": cookie}

               
            #     response1 = await client.get(url, cookies=cookies)
            #     data = response1.json()
            #     # print(data)
            #     return {"states": data}

    except Exception as error:
        return {"error": str(error)}
    


@router.get("/txn")
async def fetch_company_data(company_id: int = Query(..., description="require company id")):
    params = {
        "api_key": forecasa_api_key
    }
        
    try:
        async with httpx.AsyncClient() as client:

            url = f"https://webapp.forecasa.com/api/v1/companies/{company_id}/transactions"  
            print(url)
            response = await client.get(url, params=params)

            if response.status_code == 200:  
                data = response.json()
                return {"transactions": data.get("transactions", [])}
            # elif response.status_code == 429: 
            #     print("debug")
            #     cookie = response.headers.get("set-cookie")
            #     cookies = {"forecasa": cookie}

               
            #     response1 = await client.get(url, cookies=cookies)
            #     data = response1.json()
            #     # print(data)
            #     return {"states": data}

    except Exception as error:
        return {"error": str(error)}