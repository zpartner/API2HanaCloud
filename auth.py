import secrets as pysecrets
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config import get_vcap_credentials

security = HTTPBasic()

api_secrets = get_vcap_credentials("api2hanacloud_secrets")
API_USERNAME = api_secrets.get("API_USERNAME")
API_PASSWORD = api_secrets.get("API_PASSWORD")

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if not (
        pysecrets.compare_digest(str(credentials.username), str(API_USERNAME)) and
        pysecrets.compare_digest(str(credentials.password), str(API_PASSWORD))
    ):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials.username

