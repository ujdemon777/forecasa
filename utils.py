from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os,json,io
import pandas as pd
from cryptography.fernet import Fernet


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)



def authenticate_user(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """
    Authenticate User with Basic Authentication

    This function is used for authenticating a user with Basic Authentication. It checks the provided HTTPBasicCredentials
    against the stored username and password. If the credentials are valid, the function returns the authenticated username.

    Parameters:
        - `credentials`: HTTPBasicCredentials - The provided username and password for authentication.

    Returns:
        - If authentication is successful, returns the authenticated username.
        - If the provided credentials are invalid, raises an HTTPException with a 401 Unauthorized status.
    """

    username = os.getenv("username")
    password = os.getenv("password")

    if credentials.username != username or credentials.password != password :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username



async def encrypt_password(password):
    key = Fernet.generate_key()
    cipher_suite = Fernet(key)

    encrypted_password = cipher_suite.encrypt(password.encode('utf-8'))
    return encrypted_password,key


async def decrypt_password(key,encrypted_password):
    cipher_suite = Fernet(key)
    decrypted_password = cipher_suite.decrypt(encrypted_password).decode('utf-8')
    return decrypted_password


async def upload_file(file: UploadFile = File(...)):

    file_extension = file.filename.split(".")[-1]

    if file_extension.lower() == "json":
        contents = await file.read()
        try:
            json_data = json.loads(contents.decode("utf-8"))
            return {"msg": "JSON file received", "data": json_data, "status_code":200,"type":"json"}
        except json.JSONDecodeError:
            pass  

    elif file_extension.lower() in ["csv", "xlsx"]:
        contents = await file.read()
        try:
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
            # df.fillna(None, inplace=True)
            return {"msg": "CSV file received", "data": df.to_dict(orient='records'),"status_code":200,"type":"csv"}
        except pd.errors.ParserError:
            pass 

    return {"msg": "Unsupported file format, not csv/xlxs/json"}