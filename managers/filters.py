from fastapi import HTTPException
import os,httpx
from dotenv import load_dotenv, find_dotenv
from schemas.filters import CompanyFilters
from fastapi.responses import JSONResponse
from data import load_json


_ = load_dotenv(find_dotenv())
forecasa_api_key= os.getenv("FORECASA_API_KEY")

class Filter:
        
    def __init__(self) -> None:
        pass
    
    @classmethod
    async def fetch_filtered_company_data(cls, filters:CompanyFilters):

        try:

            data = load_json.lead_data
            companies=data.get("companies", [])

            filtered_data = companies
            print(type(filters))
            page = filters.page
            page_size = filters.page_size

            if filters.state:
                filtered_data = [company for company in companies if company.get('state') is not None and filters.state.lower() in company['state'].lower()]

            if filters.amount:
                max_value = filters.amount.get("max_value",float('inf'))
                min_value = filters.amount.get("min_value",0)
        
                filtered_data = [company for company in filtered_data if company.get('average_mortgage_amount') is not None and min_value <= company['average_mortgage_amount'] <= max_value]

            if filters.name:
                filtered_data = [company for company in filtered_data if company.get('name') is not None and filters.name.lower() in company['name'].lower()]

            if filters.transaction_tags:
                
                filter_data = []
                for company in filtered_data:
                    for tag_filter in filters.transaction_tags:
                        if company.get('tag_names') is not None and  any(tag_filter in tag for tag in company['tag_names']):
                            filter_data.append(company)
                            break
                filtered_data = filter_data
            
                
            start_index = (page-1) * page_size
            end_index = start_index + page_size

            filtered_cmp = filtered_data[start_index:end_index]
            return {"companies": filtered_cmp, "companies_total_count": len(filtered_data)}

            
        except httpx.ReadTimeout as e:
            raise HTTPException(status_code=408, detail=f"HTTP Request Timed Out:{str(e)}")
        
        except Exception as e:
            raise HTTPException(status_code=400,
                                detail=str(e))