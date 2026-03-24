from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Data Extractor Service",
    description="Serves raw source data and accepts the candidate's processed result.",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_ORIGINAL_DATA = {
    "value1": "1999/10/10 10:15:15",
    "value2": "sdfg fgfgf ffgfgrrrt sdfgsdf bmbmbmbp ",
    "value3": ["bar", "baz", "foo", "bar", "baz", 6],
    "value4": "1997/10/10 10:15:15z",
}

stored_data: dict = dict(_ORIGINAL_DATA)


@app.get("/source-data")
async def get_source_data():
    """Returns the currently stored JSON data."""
    return stored_data


@app.post("/source-data")
async def update_source_data(request: Request):
    """
    Accepts a JSON object from the candidate and stores it server-side.
    GET /source-data afterwards to verify the data was saved correctly.
    """
    global stored_data
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON"})

    if not isinstance(body, dict):
        return JSONResponse(status_code=400, content={"error": "Expected a JSON object"})

    stored_data = body
    return {"message": "Data updated successfully", "data": stored_data}


@app.post("/source-data/reset")
async def reset_source_data():
    """Resets the stored data back to the original raw source data."""
    global stored_data
    stored_data = dict(_ORIGINAL_DATA)
    return {"message": "Data reset to original", "data": stored_data}
