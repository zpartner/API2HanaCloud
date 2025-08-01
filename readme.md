# 🚀 API to SAP HANA Cloud Bridge

This FastAPI-based microservice fetches data from any public API and dynamically stores it into SAP HANA Cloud using intelligent schema inference. It includes basic authentication and a minimal set of endpoints for previewing, writing, and validating data pipelines.

---

## 🧩 Features

- 🔐 Basic Authentication via secure secrets service (`VCAP_SERVICES`)
- 📥 Extracts data from public APIs
- 🧠 Infers SAP HANA-compatible column types automatically
- 🏗️ Creates HANA tables dynamically if they don’t exist
- 💾 Inserts records with upload timestamps
- 🔍 Preview fetched API data
- 🧪 Test SAP HANA Cloud connectivity

---

## 🔧 Project Structure

```
API2HANACLOUD/
├── auth.py                # BasicAuth handling
├── hana.py                # HANA logic (connect, infer types, create table, insert)
├── main.py                # FastAPI endpoints
├── config.py              # Utility to extract credentials from VCAP_SERVICES
├── api2hanacloud_secrets.json  # Example JSON for binding user-provided secrets
├── .env.example           # Example environment config (local only)
├── manifest.yaml          # Cloud Foundry deployment
├── requirements.txt       # Python dependencies
```

---

## 📦 Installation (Local)

```bash
git clone https://github.com/YOUR_REPO/api2hanacloud.git
cd api2hanacloud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔐 Secrets Handling

In **Cloud Foundry**, secrets are managed securely through a bound user-provided service called:

```bash
api2hanacloud_secrets
```

This service injects credentials via the `VCAP_SERVICES` environment variable. Your credentials are **not** hardcoded in `manifest.yaml`.

### 🛠 Create the service

Use the included `api2hanacloud_secrets.example.json`:

```bash
cf create-user-provided-service api2hanacloud_secrets -p api2hanacloud_secrets.json
cf bind-service api2hanacloud api2hanacloud_secrets
cf restage api2hanacloud
```

Example contents of `api2hanacloud_secrets.example.json`:

```json
{
  "API_USERNAME": "admin",
  "API_PASSWORD": "secret",
  "HANA_HOST": "your-hana-host.hanacloud.ondemand.com",
  "HANA_PORT": "443",
  "HANA_USER": "your_user",
  "HANA_PASSWORD": "your_password",
  "HANA_SCHEMA": "MY_SCHEMA"
}
```

> 💡 `.env` is only used for **local testing** and is ignored in Cloud Foundry.

---

## 🚀 Running the App

### Locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### In Cloud Foundry

```bash
cf push
```

---

## 🔐 Authentication

All protected routes use **HTTP Basic Auth**. Credentials are securely loaded from the `api2hanacloud_secrets` service.

---

## 📡 API Endpoints

### `GET /`
Basic health check endpoint.

### `GET /test-hana-connection` 🔒
Tests if SAP HANA is reachable and credentials are valid.

### `POST /extract-and-write` 🔒
Fetches data from an external API and writes it to a HANA table.

**Payload:**

```json
{
  "endpoint": "https://api.example.com/data",
  "target_table": "MY_TABLE",
  "query_params": {
    "param1": "value1"
  }
}
```

### `GET /preview-data` 🔒
Previews up to 5 records from a public API endpoint.

**Query Params:**
- `endpoint=https://api.example.com/data`
- `limit=5`

### `GET /infer-types` 🔒
Infers SAP HANA-compatible types for the payload from a given API.

**Query Params:**
- `endpoint=https://api.example.com/data`
- `limit=10`

---

## 🧪 Example Test with `curl`

```bash
curl -u admin:secret http://localhost:8000/test-hana-connection
```

---

## 📜 License

MIT License.
