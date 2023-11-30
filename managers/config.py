from fastapi import HTTPException,Depends
from models.blobs import Blob
from config.db import get_db
from schemas.blobs import BlobSchema
from datetime import datetime
from sqlalchemy.orm import Session


class Config:
        
    def __init__(self) -> None:
        pass

    def create_metadata(source,filters):
        return {
            "created_at": str(datetime.utcnow()),
            "updated_at": str(datetime.utcnow()),  
            "status": source, 
            "filters": filters
        }
    
    
    @classmethod
    async def create_config(cls,user_id, payload:BlobSchema, db: Session = Depends(get_db)):
       
        try:
            existing_file= db.query(Blob).filter(Blob.file_name == payload.file_name).first()
            if existing_file:
                raise HTTPException(status_code=409,
                                    detail='file already exist')
        
            payload.created_at = str(datetime.utcnow())
            payload.updated_at = str(datetime.utcnow())
            payload.source = "forecasa"
            payload.user_id = user_id

            metadata = {
                "bronze": cls.create_metadata("bronze",payload.meta_data.bronze.filters),
                "silver": None
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
            

            payload.meta_data.silver = cls.create_metadata("sillver",payload.meta_data.silver.filters)
            
            existing_file.meta_data=payload.meta_data.model_dump()

            db.commit()

            return {"msg": "config updated successfully"}

        except HTTPException as http_exception:
            raise http_exception
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            db.close()
