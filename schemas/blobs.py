from pydantic import BaseModel
from typing import Optional


class Metadata(BaseModel):
    created_at: str = None
    updated_at: str = None
    filters: dict = None

class SourceSchema(BaseModel):
    bronze: Metadata = None
    silver: Metadata = None

class BlobSchema(BaseModel):
    file_name: str = None
    created_at: str = None
    updated_at: str = None
    meta_data: SourceSchema = None
    source: str = None
    user_id : int = None
    status : str = None
    project_label : Optional[str] = None




