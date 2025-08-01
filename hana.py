from hana_ml.dataframe import ConnectionContext
from datetime import datetime
import os
import math
from dotenv import load_dotenv

load_dotenv()

MAX_NVARCHAR_LENGTH = 5000
MIN_NVARCHAR_LENGTH = 200

def connect_hana():
    hana_host = os.getenv("HANA_HOST")
    hana_port = os.getenv("HANA_PORT")
    hana_user = os.getenv("HANA_USER")
    hana_password = os.getenv("HANA_PASSWORD")

    # Validate presence (fail early with clear message)
    if not all([hana_host, hana_port, hana_user, hana_password]):
        raise ValueError("Missing one or more SAP HANA connection environment variables.")

    conn = ConnectionContext(
        address=hana_host,
        port=int(hana_port),
        user=hana_user,
        password=hana_password,
        encrypt=True,
        sslValidateCertificate=False
    )
    cursor = conn.connection.cursor()
    return conn, cursor

def is_iso_datetime(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False

def infer_column_types(records) -> dict:
    column_types = {}
    
    for key in records[0].keys():
        values = [rec.get(key) for rec in records]
        types_seen = set()
        max_len = 0

        for val in values:
            if val is None:
                continue
            if isinstance(val, bool):
                types_seen.add("BOOLEAN")
            elif isinstance(val, int):
                types_seen.add("INTEGER")
            elif isinstance(val, float):
                types_seen.add("DOUBLE")
            elif isinstance(val, str):
                if is_iso_datetime(val):
                    types_seen.add("TIMESTAMP")
                else:
                    types_seen.add("NVARCHAR")
                    max_len = max(max_len, len(val))
            else:
                types_seen.add("NVARCHAR")
                max_len = max(max_len, len(str(val)))

        if len(types_seen) == 1:
            final_type = types_seen.pop()
        elif "NVARCHAR" in types_seen:
            final_type = "NVARCHAR"
        else:
            final_type = "NVARCHAR"

        if final_type == "NVARCHAR":
            adjusted_len = math.ceil(max_len * 1.2 / 10) * 10
            adjusted_len = min(MAX_NVARCHAR_LENGTH, max(MIN_NVARCHAR_LENGTH, adjusted_len))
            column_types[key] = f"NVARCHAR({adjusted_len})"
        else:
            column_types[key] = final_type

    return column_types

def create_table_if_needed(cursor, table: str, column_types: dict):
    schema = os.getenv("HANA_SCHEMA", "MY_SCHEMA")
    # Check if table exists
    cursor.execute(f"""
        SELECT COUNT(*) FROM TABLES 
        WHERE SCHEMA_NAME = '{schema.upper()}' 
        AND TABLE_NAME = '{table.upper()}'
    """)
    exists = cursor.fetchone()[0]

    if exists == 0:
        column_defs = ", ".join([f'"{col.upper()}" {col_type}' for col, col_type in column_types.items()])
        column_defs += ', "UPLOAD_TS" TIMESTAMP'
        create_stmt = f'CREATE COLUMN TABLE "{schema}"."{table}" ({column_defs})'
        cursor.execute(create_stmt)


def insert_records(cursor, conn, table: str, column_types: dict, records: list):
    schema = os.getenv("HANA_SCHEMA", "MY_SCHEMA")
    cols = list(column_types.keys())
    cols.append("UPLOAD_TS")

    placeholders = ", ".join(["?" for _ in cols])
    insert_stmt = f'''
        INSERT INTO "{schema}"."{table}" ({", ".join([f'"{col.upper()}"' for col in cols])})
        VALUES ({placeholders})
    '''

    for record in records:
        row = []
        for col in column_types.keys():
            val = record.get(col)
            if val is None:
                row.append(None)
            elif isinstance(val, (int, float, bool)):
                row.append(val)
            else:
                # Handle truncation
                max_length = 5000  # global cap
                string_val = str(val)
                if len(string_val) > max_length:
                    string_val = string_val[:max_length]
                row.append(string_val)

        row.append(datetime.now())
        cursor.execute(insert_stmt, row)

    conn.connection.commit()
