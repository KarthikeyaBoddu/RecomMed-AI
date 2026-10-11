from fastapi import FastAPI

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