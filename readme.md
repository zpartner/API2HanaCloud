# 🚀 API to SAP HANA Cloud Bridge

This FastAPI-based microservice fetches data from any public API and dynamically stores it into SAP HANA Cloud using intelligent schema inference. It includes basic authentication and a minimal set of endpoints for previewing, writing, and validating data pipelines.

---

## 🧩 Features

- 🔐 Basic Authentication via environment variables
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
├── .env.example           # Example environment config
├── manifest.yaml          # Cloud Foundry deployment
├── requirements.txt       # Python dependencies
```

---

## 📦 Installation

```bash
git clone https://github.com/YOUR_REPO/api2hanacloud.git
cd api2hanacloud
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Duplicate `.env.example` into `.env` and fill in your credentials:

```env
API_USERNAME=your_admin_user
API_PASSWORD=your_admin_pass

HANA_HOST=your.hana.host
HANA_PORT=443
HANA_USER=your_hana_user
HANA_PASSWORD=your_hana_password
HANA_SCHEMA=MY_SCHEMA
```

---

## 🚀 Running the App

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or with Cloud Foundry using `manifest.yaml`:

```bash
cf push
```

---

## 🔐 Authentication

All protected routes use **HTTP Basic Auth**. Use the credentials defined in your `.env` file.

---

## 📡 API Endpoints

### `GET /`
Basic health check endpoint.

### `GET /test-hana-connection`
Tests if SAP HANA is reachable and credentials are valid.

> 🔒 Protected

### `POST /extract-and-write`
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

> 🔒 Protected

### `GET /preview-data`
Previews up to 5 records from a public API endpoint.

**Query Params:**

- `endpoint=https://api.example.com/data`
- `limit=5`

> 🔒 Protected

### `GET /infer-types`
Infers SAP HANA-compatible types for the payload from a given API.

**Query Params:**

- `endpoint=https://api.example.com/data`
- `limit=10`

> 🔒 Protected

---

## 🧪 Example Test with `curl`

```bash
curl -u admin:secret http://localhost:8000/test-hana-connection
```

---

## 📜 License

MIT License.
