from fastapi import APIRouter
from endpoints import  blobs, auth, leads, transaction, filters, mail, user, contact, config

router = APIRouter()
router.include_router(transaction.router)
router.include_router(leads.router)
router.include_router(blobs.router)
router.include_router(auth.router)
router.include_router(filters.router)
router.include_router(mail.router)
router.include_router(user.router)
router.include_router(contact.router)
router.include_router(config.router)