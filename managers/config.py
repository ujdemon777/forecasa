from fastapi import HTTPException,Depends
from models.blobs import Blob
from config.db import get_db
from schemas.blobs import BlobSchema
from datetime import datetime
from sqlalchemy.orm import Session


class Config:
        
    def __init__(self) -> None:
        pass

    async def create_metadata(filters):

        filters.pop("page", None)
        filters.pop("page_size", None)
        
        return {
            "created_at": str(datetime.utcnow()),
            "updated_at": str(datetime.utcnow()),   
            "filters": filters
        }
    
    
    @classmethod
    async def create_config(cls,user_name, payload:BlobSchema, db: Session = Depends(get_db)):
       
        try:
            existing_file= db.query(Blob).filter(Blob.file_name == payload.file_name).first()
            if existing_file:
                raise HTTPException(status_code=409,
                                    detail='file already exist')
        
            payload.created_at = str(datetime.utcnow())
            payload.updated_at = str(datetime.utcnow())
            payload.source = "forecasa"
            payload.user_name = user_name
            payload.status = "bronze"

            metadata = {
                'bronze': await cls.create_metadata(payload.meta_data.bronze.filters),
                'silver' : {}
            }

            payload.meta_data = metadata


            new_file = Blob(**payload.model_dump())

            db.add(new_file)
            db.commit()
            db.refresh(new_file)

            return {"msg": "config created successfully", "file": new_file}

        except HTTPException as http_exception:
            raise http_exception
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            db.close()


    @classmethod
    async def update_config(cls,payload: BlobSchema,db: Session = Depends(get_db)):
        try:
            existing_file= db.query(Blob).filter(Blob.file_name == payload.file_name).first()
            if not existing_file:
                raise HTTPException(status_code=404, detail=f'No file with this name: {payload.file_name} found')

            existing_file.meta_data = existing_file.meta_data or {}
            
            silver_filters = await cls.create_metadata(payload.meta_data.silver.filters)

            updated_metadata = existing_file.meta_data.copy()
            updated_metadata['silver'] = silver_filters

            existing_file.meta_data = updated_metadata
            existing_file.status="silver"

            db.commit()

            return {"msg": "config updated successfully"}

        except HTTPException as http_exception:
            raise http_exception
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            db.close()
