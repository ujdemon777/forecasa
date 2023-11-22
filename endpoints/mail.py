from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from Oauth import get_current_user
from managers.mail.mail import Email
from schemas.auth import EmailVerificationRequest


router = APIRouter(
    prefix="/mail",
    tags=["Mail"],
    responses={404: {"description": "Not found"}},
)


@router.post("/send-email")
async def request_verification_code(email_verification_request: EmailVerificationRequest,
                                    current_user: str = Depends(get_current_user)):
    
    rec_email = email_verification_request.email
    try:
        mail = await Email.sendMail(rec_email)

        if mail.status_code == 200:
            return {"msg": "Verification email sent successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))