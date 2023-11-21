from fastapi import APIRouter, Depends, HTTPException,Request, Query
import json,os
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from managers.blobs import Blobs
from managers.filters import Filters
from Oauth import get_current_user
from fastapi.responses import JSONResponse


_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="",
    tags=["Blobs"],
    responses={404: {"description": "Not found"}},
)


azure_storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
azure_storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
azure_storage_file_system = os.getenv("AZURE_STORAGE_FILE_SYSTEM")
azure_storage_saas_token = os.getenv("AZURE_STORAGE_SAAS_TOKEN")


container_name = azure_storage_file_system
sas_url=azure_storage_saas_token
blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=sas_url)
        


@router.post("/blob")
async def create_blob(request:Request,current_user: str = Depends(get_current_user)):
   
    filters = await request.json()

    company = await Filters.fetch_filtered_company_data(filters)
    company["source"] = "forecasa"
    company["created_at"] = str(datetime.utcnow())
    company["filters"] = filters

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_date_time = str(datetime.utcnow())

    directory_name = f"{current_date}/"
    blob_name = f"lc_{current_date_time}.json"

    try:
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(directory_name + blob_name)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error listing files: {str(e)}")

    companies=company.get('companies' , dict())

    if not companies:
        raise HTTPException(status_code=400,
                        detail='No Companies Provided in Request')

    try:
        config_blob = await Blobs.add_config_blob(container_client,filters)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while creating config Blob: {str(e)}")

    blob_client.upload_blob(json.dumps(company), blob_type="BlockBlob",overwrite=True)

    return {"msg": "company_ids added successfully"}



@router.get("/blobs")
async def get_blobs(current_user: str = Depends(get_current_user)):
    try:
        container_client = blob_service_client.get_container_client(container_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get the blob list. Error: {str(e)}")
    
    blob_list = container_client.list_blobs()

    blobs=[]
    for blob in blob_list:
        blobs.append(f"File Name: {blob.name}")
    return {"msg": f"{len(blobs)} blobs retrieved", "blobs": blobs}

    

@router.get("/blob")
async def get_particular_blob(blob: str = Query(..., description="requires name of particular blob"),
                    current_user: str = Depends(get_current_user)):
    
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get the blob, Error: {str(e)}")
    
    if blob_client.exists():
        downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
        blob = json.loads(downloader.readall())

        return {"msg": f"blobs retrieved successfully", "blob": blob}
    
    else:
        raise HTTPException(status_code=400, detail=f"No Blob Found for {blob}")

    

@router.delete("/blob")
async def delete_particular_blob(blob: str = Query(..., description="requires name of particular blob"),
                                 current_user: str = Depends(get_current_user)):

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get the blob, Error: {str(e)}")
    
    if blob_client.exists():
        blob_client.delete_blob()

        return {"message": f"Blob {blob} deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail=f"No Blobs Found")
    
    