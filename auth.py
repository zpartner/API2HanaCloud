import os
import secrets
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "secret")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        secrets.compare_digest(credentials.username, API_USERNAME) and
        secrets.compare_digest(credentials.password, API_PASSWORD)
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username
