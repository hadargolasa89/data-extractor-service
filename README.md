# Data Extractor Service

Backend service for the **Data Extractor** home assignment.  
Live at: **`https://data-extractor-service.onrender.com`**

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/source-data` | Returns the raw, messy JSON the candidate must transform |
| `POST` | `/source-data` | Upload the candidate's processed result to store it server-side |
| `POST` | `/source-data/reset` | Reset stored data back to the original raw data |
| `GET` | `/docs` | Interactive Swagger UI |

---

## Usage

### 1. Fetch the raw source data
```bash
curl https://data-extractor-service.onrender.com/source-data
```

### 2. POST your processed result
```bash
curl -X POST https://data-extractor-service.onrender.com/source-data \
  -H "Content-Type: application/json" \
  -d '{
    "value1": "2021/10/10 10:15:15",
    "value2": "pbmbmbmbfdsgsfdstrrrgrfgfffgfgfgfgfds",
    "value3": ["bar", "baz", "foo", 5],
    "value4": "z51:51:0101/01/7991"
  }'
```

### 3. GET again to verify it was stored
```bash
curl https://data-extractor-service.onrender.com/source-data
```

### 4. Reset when done
```bash
curl -X POST https://data-extractor-service.onrender.com/source-data/reset
```

> ⚠️ Storage is **in-memory** — resets automatically when the service restarts (Render free tier sleeps after 15 min idle). First request after idle takes ~30s to wake up.

---

## Run Locally

```bash
pip install -r requirements.txt
python3 -m uvicorn main:app --reload
```

---

## Deploy to Render (free)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/hadargolasa89/data-extractor-service)

1. Go to [render.com](https://render.com) → sign up with GitHub.
2. Click the button above — Render reads `render.yaml` and pre-fills all settings.
3. Click **Create Resources** — live in ~2 min.
