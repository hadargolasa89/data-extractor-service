from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Data Extractor Service",
    description="Returns the raw source JSON the candidate must consume and transform.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCE_DATA = {
    "value1": "1999/10/10 10:15:15",
    "value2": "sdfg fgfgf ffgfgrrrt sdfgsdf bmbmbmbp",
    "value3": ["bar", "baz", "foo", "bar", "baz", 5],
    "value4": "1997/10/10 10:15:15z",
}


@app.get("/source-data")
async def source_data():
    """Returns the raw, messy JSON the candidate needs to consume and transform."""
    return SOURCE_DATA
