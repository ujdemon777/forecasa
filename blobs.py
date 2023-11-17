from fastapi import HTTPException
from models.response import Response
import json
from datetime import datetime


class Blobs:
        
    def __init__(self) -> None:
        pass

    async def add_companies_blob(container_client,company_ids):

        try:
        
            blob_client = container_client.get_blob_client("company_blob.json")

            data={}
            data["companies"]=company_ids
            data["source"] = "forecasa"
            data["created_at"] = str(datetime.utcnow())

            
            if not blob_client.exists():
                blob_client.upload_blob(json.dumps(data), blob_type="BlockBlob",overwrite=True)
                return company_ids
            else:
                downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
                blob_text = downloader.readall()
                existing_data = json.loads(blob_text) if blob_text else []

                existing_company_ids = set(existing_data.get("companies", []))
                unique_company_ids = list(set(company_ids) - existing_company_ids)
                existing_data["companies"] = existing_data.get("companies", []) + unique_company_ids

                blob_client.upload_blob(json.dumps(existing_data), blob_type="BlockBlob", overwrite=True)
                return unique_company_ids

            
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get the blob in the container. Error: {str(e)}")
        
        

    async def add_config_blob(container_client):
        try:

            blob_client = container_client.get_blob_client("config_blob.json")

            data={}
            data["source"] = "forecasa"
            data["created_at"] = str(datetime.utcnow())

            
            if not blob_client.exists():
                blob_client.upload_blob(json.dumps(data), blob_type="BlockBlob",overwrite=True)
                return Response(data, f"config blob created successfully." , 200 , False)
            else:
                downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
                blob_text = downloader.readall()
                existing_data = json.loads(blob_text) if blob_text and blob_text.startswith("[") else [json.loads(blob_text)]
                existing_data.append(data)  
                blob_client.upload_blob(json.dumps(existing_data), blob_type="BlockBlob", overwrite=True)
                return Response(data, f"companies added successfully." , 200 , False)

            
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get the blob in the container. Error: {str(e)}")