from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from data_extractor import process_data

app = FastAPI(
    title="Data Extractor Service",
    description=(
        "Reference backend for the Data Extractor home assignment. "
        "POST your JSON to /process and receive the correctly processed output."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Meta"])
async def health():
    return {"status": "ok"}


@app.post("/process", tags=["Data"])
async def process(request: Request):
    """
    Accepts a flat JSON object and returns the processed version:
    - **Datetime strings** (`YYYY/MM/DD HH:mm:ss`): year changed to 2021
    - **Other strings**: all whitespace removed, then reversed
    - **Lists**: duplicates removed (order preserved)
    - **Invalid JSON body**: returns `{"error": "Bad input"}`
    """
    try:
        data = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Bad input"})

    if not isinstance(data, dict):
        return JSONResponse(status_code=400, content={"error": "Bad input"})

    return process_data(data)
