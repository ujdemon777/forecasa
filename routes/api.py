from fastapi import APIRouter
from endpoints import  company, company_warehouse, auth, transaction, filters, mail

router = APIRouter()
router.include_router(transaction.router)
router.include_router(company.router)
router.include_router(company_warehouse.router)
router.include_router(auth.router)
router.include_router(filters.router)
router.include_router(mail.router)