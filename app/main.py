from fastapi import FastAPI
from pydantic import BaseModel
from app.core.rxnorm_client import search_medicine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RecomMed AI",
    description="AI-assisted medication safety screening",
    version="0.1.0",
)

@app.get("/")
def home():
    return {
        "message" : "Welcome to RecomMed AI",
        "status": "running",
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

class MedicineSearchRequest(BaseModel):
    name: str


@app.post("/api/medicines/search")
def medicine_search(request: MedicineSearchRequest):
    return search_medicine(request.name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)