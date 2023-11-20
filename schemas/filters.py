from pydantic import BaseModel
from typing import Optional


class CompanyFilters(BaseModel):
    name: Optional[str] = None
    transaction_type: Optional[list] = None
    transaction_tags: Optional[list] = None
    counties: Optional[list] = None
    amount: Optional[dict]= None
    page: Optional[int] = 1
    page_size: Optional[int] = 500000