from fastapi import APIRouter
from endpoints import  blobs, auth, leads, transaction, filters, mail

router = APIRouter()
router.include_router(transaction.router)
router.include_router(leads.router)
router.include_router(blobs.router)
router.include_router(auth.router)
router.include_router(filters.router)
router.include_router(mail.router)