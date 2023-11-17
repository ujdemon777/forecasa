from fastapi import APIRouter, Depends, HTTPException, status, Request, Query, Body
from models.response import Response,ErrorResponse
import json,os
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobServiceClient
from datetime import datetime
from blobs import Blobs




_ = load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/cw",
    tags=[""],
    responses={404: {"description": "Not found"}},
)


azure_storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
azure_storage_account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")
azure_storage_file_system = os.getenv("AZURE_STORAGE_FILE_SYSTEM")
azure_storage_saas_token = os.getenv("AZURE_STORAGE_SAAS_TOKEN")

# adls_client = DataLakeServiceClient(account_url=f"https://{azure_storage_account_name}.dfs.core.windows.net", credential=azure_storage_account_key)



@router.post("/blob")
async def create_blob(request:Request):
    try:

        data = await request.json()
        data["source"] = "forecasa"
        data["created_at"] = str(datetime.utcnow())
        data["filters"] = None

        container_name = azure_storage_file_system

        sas_url= azure_storage_saas_token
        blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=sas_url)

        current_date = datetime.now().strftime("%Y-%m-%d")
        current_date_time = str(datetime.utcnow())
        local_path = os.path.join("./data", current_date)
        directory_name = f"{current_date}/"
        blob_name = f"forecasaa_{current_date_time}.json"
    
        container_client = blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(directory_name + blob_name)

        companies=data.get('companies' , dict())

        if not companies:
            return ErrorResponse("No companies provided in the request", 400 , False)

        company_ids = []

        for cmp in companies:
            company_ids.append(cmp.get('id'))
        

        try:
            unique_company_ids = await Blobs.add_companies_blob(container_client,company_ids)
            print("company Blob added successfully for these",unique_company_ids)
            await Blobs.add_config_blob(container_client)
            print("config Blob added successfully")
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while creating Company Blob: {str(e)}")

        filtered_companies = [company for company in data["companies"] if company["id"] in unique_company_ids]
        print("filtered_companies",filtered_companies)
        data["companies"] = filtered_companies

        print(data)

        if not os.path.exists(local_path):
            os.makedirs(local_path)
        else:
            print("Directory already exists.")

        local_file_name = str('forecasa') + ".json"
        upload_file_path = os.path.join(local_path, local_file_name)

        file = open(file=upload_file_path, mode='w')
        file.write(json.dumps(data))
        file.close()

        with open(file=upload_file_path, mode="rb") as data:
            f = data.read()
            blob_client.upload_blob(f, blob_type="BlockBlob",overwrite=True)

        print("Blob created successfully.")

       


        return Response(company_ids, "forecasa data added successfully", 200, False)


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")


@router.get("/blobs")
async def read_blob():
    try:
        container_name = azure_storage_file_system
        sas_url=azure_storage_saas_token

        blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=sas_url)
        
        container_client = blob_service_client.get_container_client(container_name)

        blob_list = container_client.list_blobs()
        # name_starts_with="123/"
        blobs=[]
        for blob in blob_list:
            print(f"File Name: {blob.name}")
            blobs.append(f"File Name: {blob.name}")
        return Response(blobs, f"{len(blobs)} blobs retrieved successfully." , 200 , False)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get the blob list in the container. Error: {str(e)}")



@router.get("/blob")
async def read_particular_blob(blob_name: str = Query(..., description="name of particular blob")):
    try:
       
        container_name = azure_storage_file_system

        sas_url=azure_storage_saas_token

        blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=sas_url)
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        if blob_client.exists():
            downloader = blob_client.download_blob(max_concurrency=1, encoding='UTF-8')
            blob_text = downloader.readall()
            blob_json = json.loads(blob_text)

            return Response(blob_json, f"companies retrieved successfully." , 200 , False)
        
        else:
            return ErrorResponse("No blobs found", 400 , False)

    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get the blob in the container. Error: {str(e)}")
    

@router.delete("/blob")
async def delete_particular_blob(blob_name: str = Query(..., description="name of blob")):
    try:
       
        container_name = azure_storage_file_system

        sas_url=azure_storage_saas_token

        blob_service_client = BlobServiceClient(account_url=f"https://{azure_storage_account_name}.blob.core.windows.net", credential=sas_url)
        
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        if blob_client.exists():
            blob_client.delete_blob()

            return Response("", f"blob deleted successfully." , 200 , False)
        else:
            return ErrorResponse("No blobs found", 400 , False)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete the blob Error: {str(e)}")