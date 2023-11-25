from fastapi import APIRouter, Depends, HTTPException
from Oauth import get_current_user
from managers.mail.mail import Email
from schemas.user import EmailVerificationRequest


router = APIRouter(
    prefix="/mail",
    tags=["Mail"],
    responses={404: {"description": "Not found"}},
)


@router.post("/send-email")
async def request_verification_code(email_verification_request: EmailVerificationRequest,
                                    current_user: str = Depends(get_current_user)):
    try:
        rec_email = email_verification_request.email
        if not rec_email:
                raise HTTPException(status_code=400, detail="Email is required")
    
        if rec_email:
            sent_mail = await Email.sendMail(rec_email)

            if sent_mail.get('status_code') == 200:
                return {"msg": "Verification email sent successfully"}
            
    except HTTPException as http_exception:
        raise http_exception
       
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))