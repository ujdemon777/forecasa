import hashlib
from fastapi import APIRouter, Body, Depends, HTTPException,Request, Query,File, UploadFile
import json,os
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from sqlalchemy import or_
from requests import Session
from config.db import get_db
from managers.blobs import Blobs
from managers.filters import Filter
from Oauth import get_current_user
from managers.config import Config
from models.company import Company
from models.leads import Leads
from models.user import Blob
from models.user import User
from schemas.blobs import BlobSchema, Metadata, SourceSchema
from utils import upload_file


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
        


async def fetch_company(file: UploadFile = File(...)):
    
    response = await upload_file(file)
    companies = []
    if response.get("status_code") == 200:
        if response.get("type") == "json":
            companies=response.get('data' , dict()).get("companies",[])

        elif response.get("type") == "csv" or response.get("type") == "xlsx":
            companies=response.get('data',[])

    if not companies:
        return {"msg":"No Companies Provided in request"}
    
    return {"companies": companies, "companies_total_count": len(companies)}
    

@router.post("/blob")
async def create_blob(request:Request,project_label:str = Body(None),file: UploadFile = File(None),current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    
    if file:
        company = await fetch_company(file)
        filters = {'user_upload_filters': 'user_upload_filters'}
        project_label = project_label
        print(project_label)
        company["filters"] = filters
    else:
        data = await request.json()
        filters = data.get('filters') or {}
        project_label = data.get('project_label')
        company = await Filter.fetch_filtered_company_data(filters)

        company["filters"] = filters 


    company["source"] = "forecasa"
    company["created_at"] = str(datetime.utcnow())
    

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
    
    company_ids = []
    company_names = []

    for cmp in companies:
        company_ids.append(cmp.get('id'))
        company_names.append(cmp.get('name'))

    existing_data = db.query(Leads.company_id, Leads.company_name).filter(
    or_(
        Leads.company_id.in_(set(company_ids)),
        Leads.company_name.in_(set(company_names))
    )
    ).all()

    existing_company_ids = [company_id[0] for company_id in existing_data]
    # unique_company_ids = list(set(company_ids) - set(existing_company_ids))

    existing_company_names = [company_name[1] for company_name in existing_data]
    # unique_company_names = list(set(company_names) - set(existing_company_names))

    unique_company_ids = []
    unique_company_names = []
    
    for company_id, company_name in zip(company_ids, company_names):
        if company_id not in existing_company_ids and company_name not in existing_company_names:
            unique_company_ids.append(company_id)
            unique_company_names.append(company_name)

    # existing_company_ids = [company_id[0] for company_id in db.query(Leads.company_id).filter(Leads.company_id.in_(set(company_ids))).all()]
    # unique_company_ids = list(set(company_ids) - set(existing_company_ids))

    # existing_company_names = [company_name[0] for company_name in db.query(Leads.company_name).filter(Leads.company_name.in_(set(company_names))).all()]
    # unique_company_names = list(set(company_names) - set(existing_company_names))

    company_key = [hashlib.sha256(f'{company_id}-{company_name}'.encode()).hexdigest() for company_id, company_name in zip(unique_company_ids, unique_company_names)]
    
    db.bulk_insert_mappings(Leads, [{'company_key': key, 'company_id':company_id, 'company_name':company_name, 'status': 'bronze'} for key,company_id,company_name in zip(company_key,unique_company_ids,unique_company_names)])
    db.commit()
    
    # try:
    #     config_blob = await Blobs.add_config_blob(container_client,filters)
    
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=f"Error while creating config Blob: {str(e)}")

    try:
        meta_data = Metadata(created_at="", updated_at="", filters=filters) 
        source_schema = SourceSchema(bronze=meta_data,silver=meta_data)
        payload = BlobSchema(file_name=blob_name,meta_data=source_schema,project_label=project_label)

        existing_file= db.query(Blob).filter(Blob.file_name == blob_name).first()

        if not existing_file:
            config_blob = await Config.create_config(current_user.id,payload,db)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error while creating config Blob: {str(e)}")
   
    blob_client.upload_blob(json.dumps(company), blob_type="BlockBlob",overwrite=True)

    return {"msg": "company_ids added successfully","config_blog":config_blob}



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
    


    

    

    