from fastapi import APIRouter, Depends, HTTPException,Query,Body
from fastapi.responses import JSONResponse
import os,httpx
from dotenv import load_dotenv, find_dotenv
from schemas.filters import CompanyFilters
from Oauth import get_current_user
import json

_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/company",
    tags=["Filters"],
    responses={404: {"description": "Not found"}},
)

forecasa_api_key= os.getenv("FORECASA_API_KEY")



@router.post("/filter")
async def fetch_company_data(filters: CompanyFilters,
                             current_user: str = Depends(get_current_user)):
    params = {
        "api_key": forecasa_api_key
    }

    if filters.page:
        params[f"page"] = filters.page

    if filters.page_size:
        params[f"page_size"] = filters.page_size

    if filters.transaction_tags:
        params[f"q[tags_name_in][]"] = filters.transaction_tags

    if filters.name:
        params["q[name_cont]"] = filters.name

    if filters.counties:
        params["[transactions][q][county_in][]"] = filters.counties

    if filters.transaction_type:
        params[f"[transactions][q][transaction_type_in][]"] = filters.transaction_type

    if filters.amount:
        if filters.amount.get("max_value"):
            params[f"transactions[q][amount_lteq]"] = filters.amount.get("max_value")
        if filters.amount.get("min_value"):
            params[f"transactions[q][amount_gteq]"] = filters.amount.get("min_value")
        
    try:
        async with httpx.AsyncClient() as client:

            url = "https://webapp.forecasa.com/api/v1/companies"  
            response = await client.get(url, params=params, timeout=10)

            if response.status_code == 200:  
                companies = response.json()
                return JSONResponse({"companies": companies.get("companies", []), "companies_total_count": companies.get("companies_total_count", 0)})
            
    except httpx.ReadTimeout as e:
        raise HTTPException(status_code=408, detail=f"HTTP Request Timed Out:{str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))
    


@router.get("/txn")
async def fetch_company_txn_data(company_id: int = Query(..., description="requires company id"),
                                 current_user: str = Depends(get_current_user)):
    params = {
        "api_key": forecasa_api_key
    }
        
    try:
        async with httpx.AsyncClient() as client:

            url = f"https://webapp.forecasa.com/api/v1/companies/{company_id}/transactions"  
            response = await client.get(url, params=params)

            if response.status_code == 200:  
                company_transaction = response.json()
                return JSONResponse({"transactions": company_transaction.get("transactions", [])})

    except httpx.ReadTimeout as e:
        raise HTTPException(status_code=408, detail=f"HTTP Request Timed Out:{str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))
    




@router.get("/forecasa/states")
async def fetch_states():
    params = {"api_key": forecasa_api_key}  

    try:
        async with httpx.AsyncClient() as client:

            url = "https://webapp.forecasa.com/api/v1/geo/counties_by_states"  
            response = await client.get(url, params=params)


            if response.status_code == 200:  
                data = response.json()
                return {"states": data}
            elif response.status_code == 429: 
                print("debug")
                cookie = response.headers.get("set-cookie")
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
    params={"q[tags_name_in][]":body.get('company_tags'),"[transactions][q][county_in][]":body.get('counties'),"q[name_cont]":body.get('company_name'),"api_key": forecasa_api_key}
   

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
                return {"states": data}
