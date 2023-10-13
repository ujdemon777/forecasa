from fastapi import APIRouter
from endpoints import  forecasa, company

router = APIRouter()
router.include_router(forecasa.router)
router.include_router(company.router)
