from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import os

from auth import authenticate, security
from hana import (
    connect_hana,
    infer_column_types,
    create_table_if_needed,
    insert_records,
)

app = FastAPI(title="Generic API-to-HANA Bridge")

class GenericAPIPayload(BaseModel):
    endpoint: str
    target_table: str
    query_params: Optional[Dict[str, Any]] = None

@app.get("/")
def hello_world():
    """
    Public endpoint to check API health.
    """
    return {"message": "Hello from HanaBridge API 👋"}

@app.get("/test-hana-connection", dependencies=[Depends(authenticate)])
def test_hana_connection():
    """
    Secure endpoint to test SAP HANA Cloud connection.
    Executes a simple SELECT statement to verify connectivity.
    """
    try:
        conn, cursor = connect_hana()
        cursor.execute("SELECT 1 FROM DUMMY")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"status": "success", "hana_response": result[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HANA connection failed: {str(e)}")

@app.post("/extract-and-write", dependencies=[Depends(authenticate)])
async def extract_and_write(payload: GenericAPIPayload):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(payload.endpoint, params=payload.query_params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API data: {str(e)}")

    records = data if isinstance(data, list) else [data]
    if not records or not isinstance(records[0], dict):
        raise HTTPException(status_code=400, detail="Invalid API response structure")

    conn, cursor = connect_hana()
    table = payload.target_table.upper()

    column_types = infer_column_types(records)
    create_table_if_needed(cursor, table, column_types)
    insert_records(cursor, conn, table, column_types, records)

    cursor.close()
    conn.close()

    return {"message": f"{len(records)} records inserted into {table}"}

@app.get("/preview-data", dependencies=[Depends(authenticate)])
async def preview_data(endpoint: str, limit: int = 5):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)
        response.raise_for_status()
        data = response.json()
        records = data if isinstance(data, list) else [data]
        return {"preview": records[:limit]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch preview: {str(e)}")

@app.get("/infer-types", dependencies=[Depends(authenticate)])
async def infer_types(endpoint: str, limit: int = 10):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)
        response.raise_for_status()
        data = response.json()
        records = data if isinstance(data, list) else [data]
        column_types = infer_column_types(records[:limit])
        return {"inferred_types": column_types}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to infer types: {str(e)}")
