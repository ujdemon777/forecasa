from fastapi import APIRouter
from endpoints import  forecasa, company, company_warehouse

router = APIRouter()
router.include_router(forecasa.router)
router.include_router(company.router)
router.include_router(company_warehouse.router)
