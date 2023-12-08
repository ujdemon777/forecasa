from fastapi import APIRouter, Depends, HTTPException,Query,Body
import os,httpx
from schemas.filters import CompanyFilters
from Oauth import get_current_user
import json
from data import load_json
import datetime


router = APIRouter(
    prefix="/company",
    tags=["Filters"],
    responses={404: {"description": "Not found"}},
)

forecasa_api_key= os.getenv("FORECASA_API_KEY")



@router.post("/filter")
async def fetch_company_data(filters: CompanyFilters):
    # params = {
    #     "api_key": forecasa_api_key
    # }

    # if filters.page:
    #     params[f"page"] = filters.page

    # if filters.page_size:
    #     params[f"page_size"] = filters.page_size

    # if filters.transaction_tags:
    #     params[f"q[tags_name_in][]"] = filters.transaction_tags

    # if filters.name:
    #     params["q[name_cont]"] = filters.name

    # if filters.counties:
    #     params["[transactions][q][county_in][]"] = filters.counties

    # if filters.transaction_type:
    #     params[f"[transactions][q][transaction_type_in][]"] = filters.transaction_type

    # if filters.amount:
    #     if filters.amount.get("max_value"):
    #         params[f"transactions[q][amount_lteq]"] = filters.amount.get("max_value")
    #     if filters.amount.get("min_value"):
    #         params[f"transactions[q][amount_gteq]"] = filters.amount.get("min_value")
        
    try:
        # async with httpx.AsyncClient() as client:

        #     url = "https://webapp.forecasa.com/api/v1/companies"  
        #     response = await client.get(url, params=params, timeout=10)

        #     if response.status_code == 200:
        #         companies = response.json() 
        #         return {"companies": companies.get("companies", []), "companies_total_count": companies.get("companies_total_count", 0)}
        
        data = load_json.company_data
        companies=data.get("companies", [])

        filtered_data = companies

        if filters.amount:
            max_value = filters.amount.get("max_value",float('inf'))
            min_value = filters.amount.get("min_value",0)
    
            filtered_data = [company for company in companies if company['average_mortgage_amount'] >= min_value and company['average_mortgage_amount'] <= max_value ]

        if filters.name:
            filtered_data = [company for company in filtered_data if filters.name.lower() in company['name'].lower()]

        if filters.transaction_tags:
            
            filter_data = []
            for company in filtered_data:
                for tag_filter in filters.transaction_tags:
                    if any(tag_filter in tag for tag in company['tag_names']):
                        filter_data.append(company)
                        break
            filtered_data = filter_data
          
            # [company for company in filtered_data if any(filters.transaction_tags in tag for tag_filter in filters.transaction_tags for tag in company['tag_names'])]
            # filtered_data = [company for company in companies if any(filters.transaction_tags in tag for tag in company['tag_names'])]
            # filtered_data = [company for company in filtered_data if filters.transaction_tags[0] in [tag for tag in company['tag_names']]]

        # if filters.mortgage_transactions:
        #     max_value = filters.mortgage_transactions.get("max_value",float('inf'))
        #     min_value = filters.mortgage_transactions.get("min_value",0)

        #     filtered_data = [company for company in filtered_data if company['mortgage_transactions'] > min_value and company['mortgage_transactions'] < max_value ]

        # if filters.last_transaction_date:
        #     start_date = filters.last_transaction_date.get("start_date")
        #     end_date = filters.last_transaction_date.get("end_date")

        #     if end_date is None:
        #         end_date = datetime.datetime.now().strftime('%Y-%m-%d')

        #     filtered_data = [company for company in filtered_data if (start_date is None or company['last_transaction_date'] >= start_date) and company['last_transaction_date'] <= end_date]

        return {"companies": filtered_data, "companies_total_count": len(filtered_data)}

            
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
        # async with httpx.AsyncClient() as client:

            # url = f"https://webapp.forecasa.com/api/v1/companies/{company_id}/transactions"  
            # response = await client.get(url, params=params)

            # if response.status_code == 200:  
        company_transaction = load_json.txn_data
        return {"transactions": company_transaction.get("transactions", [])}

    except httpx.ReadTimeout as e:
        raise HTTPException(status_code=408, detail=f"HTTP Request Timed Out:{str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=str(e))
    




# @router.get("/forecasa/states")
# async def fetch_states():
#     params = {"api_key": forecasa_api_key}  

#     try:
#         async with httpx.AsyncClient() as client:

#             url = "https://webapp.forecasa.com/api/v1/geo/counties_by_states"  
#             response = await client.get(url, params=params)


#             if response.status_code == 200:  
#                 data = response.json()
#                 return {"states": data}
#             elif response.status_code == 429: 
#                 print("debug")
#                 cookie = response.headers.get("set-cookie")
#                 cookies = {"forecasa": cookie}

               
#                 response1 = await client.get(url, cookies=cookies)
#                 data = response1.json()
#                 # print(data)
#                 return {"states": data}

#     except Exception as error:
#         return {"error": str(error)}



# @router.post("/forecasa/fetch_company_data")
# async def fetch_company_data(
#     body = Body(None, description="List of categories to filter"),
#     # company_name: string = Query(None, description="List of categories to filter"),
#     # counties: list = Body(None, description="List of categories to filter")
# ):
#     params={"q[tags_name_in][]":body.get('company_tags'),"[transactions][q][county_in][]":body.get('counties'),"q[name_cont]":body.get('company_name'),"api_key": forecasa_api_key}
   

#     async with httpx.AsyncClient() as client:

#         url = "https://webapp.forecasa.com/api/v1/companies"  
#         response = await client.get(url, params=params)

#         if response.status_code == 200:
#             try:
#                 data = response.json()
#                 return data
#             except json.JSONDecodeError:
#                 raise HTTPException(status_code=500, detail="Error parsing JSON data from the API")
            
#         elif response.status_code == 429: 
#                 cookie = response.headers.get("set-cookie")
#                 cookies = {"forecasa": cookie}

#                 params.pop('api_key')
#                 response1 = await client.get(url, cookies=cookies,params=params)
#                 data = response1.json()
#                 return {"states": data}
