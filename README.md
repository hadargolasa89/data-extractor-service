# Data Extractor Service

A free reference backend for the **Data Extractor** home assignment.  
Send your JSON to the `/process` endpoint and receive the correctly processed output.

## Live API

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/process` | Process a JSON object |
| `GET` | `/docs` | Interactive Swagger UI |

---

## Processing Rules

| Value type | Transformation |
|-----------|----------------|
| String matching `YYYY/MM/DD HH:mm:ss` | Year changed to **2021** |
| Other strings | All whitespace removed, then **reversed** |
| Lists | **Duplicates removed** (order preserved) |
| Numbers / booleans / null | Unchanged |

---

## Example

**Request**
```bash
curl -X POST https://<your-service>.onrender.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "value1": "1999/10/10 10:15:15",
    "value2": "sdfg fgfgf ffgfgrrrt sdfgsdf bmbmbmbp",
    "value3": ["bar", "baz", "foo", "bar", "baz", 5],
    "value4": "1997/10/10 10:15:15z"
  }'
```

**Response**
```json
{
  "value1": "2021/10/10 10:15:15",
  "value2": "pbmbmbmbfdsgsfdstrrrgrfgfffgfgfgfgfds",
  "value3": ["bar", "baz", "foo", 5],
  "value4": "z51:51:0101/01/7991"
}
```

> `value4` has a trailing `z` so it does **not** match the datetime format — it is treated as a plain string.

---

## Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open http://localhost:8000/docs for the interactive API docs.

## Run Tests

```bash
# pytest e2e tests
pytest tests/test_e2e.py -v

# unittest tests
python -m pytest tests/test_unit.py -v
# or
python -m unittest discover -s tests -p "test_unit.py"
```

---

## Project Layout

```
.
├── data_extractor.py   # DataExtractor class + shared processing logic
├── main.py             # FastAPI web service
├── tests/
│   ├── test_e2e.py     # pytest end-to-end tests (HTTP layer)
│   └── test_unit.py    # unittest tests (DataExtractor class)
├── requirements.txt
└── render.yaml         # Render deployment config
```

---

## Deploy to Render (free)

1. Push this repo to GitHub.
2. Go to [render.com](https://render.com) → **New Web Service** → connect your repo.
3. Render picks up `render.yaml` automatically — click **Deploy**.
4. Your service will be live at `https://<name>.onrender.com`.
