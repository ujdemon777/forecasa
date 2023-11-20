from fastapi import HTTPException
import os,httpx
from dotenv import load_dotenv, find_dotenv
from schemas.filters import CompanyFilters
from fastapi.responses import JSONResponse


_ = load_dotenv(find_dotenv())
forecasa_api_key= os.getenv("FORECASA_API_KEY")

class Filters:
        
    def __init__(self) -> None:
        pass

    async def fetch_filtered_company_data(filters: CompanyFilters):

        filters = CompanyFilters.model_validate(filters)
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
                response = await client.get(url, params=params)

                if response.status_code == 200:  
                    data = response.json()
                    return JSONResponse({"companies": data.get("companies", []), "companies_total_count": data.get("companies_total_count", 0)})

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))