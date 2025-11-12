# fastapi_app.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
from main import ask_sanhuri

app = FastAPI(title="Sanhuri AI Research Assistant")

# Optional root endpoint
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Sanhuri AI Research Assistant API!"}

# POST endpoint (JSON input)
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(request: QueryRequest):
    response = ask_sanhuri(request.query)
    return response

# GET endpoint (query parameter input)
@app.get("/ask")
async def ask(query: str = Query(..., description="The question to ask the AI")):
    response = ask_sanhuri(query)
    return response
