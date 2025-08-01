import os
import json

def get_vcap_credentials(service_name: str) -> dict:
    vcap = os.getenv("VCAP_SERVICES")
    if not vcap:
        raise RuntimeError("VCAP_SERVICES not found in environment.")

    services = json.loads(vcap)
    for svc in services.get("user-provided", []):
        if svc["name"] == service_name:
            return svc["credentials"]

    raise RuntimeError(f"Service {service_name} not found in VCAP_SERVICES.")
