from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.analysis_service import (
    analyze_startup_idea
)

app = FastAPI(
    title="Saasify API",
    description="AI Startup Intelligence Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class AnalysisRequest(BaseModel):
    idea: str


@app.get("/")
def health():

    return {
        "status": "healthy",
        "service": "saasify",
        "version": "2.0.0"
    }


@app.post("/analyze")
def analyze(
    request: AnalysisRequest
):

    return analyze_startup_idea(
        request.idea
    )