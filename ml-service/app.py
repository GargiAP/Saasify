from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import faiss
import pickle
import json
import os
from sentence_transformers import SentenceTransformer
from llmservice import analyze_idea_with_llm
from gapanalysis import analyze_gaps
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Saasify ML API",
    description="AI-powered startup idea evaluation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

print("Loading models and data...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
faiss_index = faiss.read_index("models/products.index")
df = pd.read_csv("data/products_clean.csv")

with open("models/viability_model.pkl", "rb") as f:
    viability_model = pickle.load(f)

with open("models/shap_explainer.pkl", "rb") as f:
    shap_explainer = pickle.load(f)

with open("models/feature_cols.pkl", "rb") as f:
    feature_cols = pickle.load(f)

with open("models/metrics.json", "r") as f:
    model_metrics = json.load(f)

print("All models loaded successfully!")

print("Pre-computing competitor keywords...")
class IdeaRequest(BaseModel):
    idea: str

class FeedbackRequest(BaseModel):
    idea: str
    score: int
    helpful: bool
    comment: str = ""

def get_similar_products(idea: str, top_k: int = 8):
    idea_embedding = embedding_model.encode([idea])
    idea_embedding = np.array(idea_embedding).astype("float32")
    faiss.normalize_L2(idea_embedding)
    scores, indices = faiss_index.search(idea_embedding, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "name": str(df.iloc[idx]["name"]),
            "tagline": str(df.iloc[idx]["tagline"]),
            "similarity": round(float(score), 3)
        })
    return results

def compute_features_for_idea(idea: str, similar_products: list):
    competition_density = float(np.mean([
        p["similarity"] for p in similar_products
    ]))
    novelty_score = round(1.0 - competition_density, 4)

    high_growth = [
        "ai", "automation", "saas", "developer",
        "analytics", "productivity", "fintech", "health"
    ]
    idea_lower = idea.lower()
    market_growth = min(1.0, sum(
        1 for w in high_growth if w in idea_lower
    ) * 0.15 + 0.2)

    pain_words = [
        "frustrat", "difficult", "hard to", "struggle",
        "problem", "issue", "slow", "manual", "expensive",
        "time-consuming", "complex", "broken", "inefficient"
    ]
    pain_severity = min(1.0, sum(
        1 for w in pain_words if w in idea_lower
    ) * 0.15 + 0.2)

    monetization_words = [
        "subscription", "enterprise", "b2b", "saas",
        "business", "payment", "premium", "team", "api"
    ]
    monetization_signal = min(1.0, sum(
        1 for w in monetization_words if w in idea_lower
    ) * 0.12 + 0.2)

    description_quality = min(1.0, len(idea) / 200)

    topic_diversity = min(1.0, len(idea.split()) / 20)

    return {
        "competition_density": competition_density,
        "novelty_score": novelty_score,
        "market_growth": market_growth,
        "pain_severity": pain_severity,
        "monetization_signal": monetization_signal,
        "description_quality": description_quality,
        "topic_diversity": topic_diversity
    }

def compute_viability(features: dict):
    features_df = pd.DataFrame([features])[feature_cols]
    raw_score = float(viability_model.predict(features_df)[0])
    raw_score = np.clip(raw_score, 0, 1)
    score_100 = int(raw_score * 100)

    shap_values = shap_explainer.shap_values(features_df)[0]
    shap_breakdown = sorted(
        zip(feature_cols, shap_values),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    shap_list = [
        {"feature": feat, "value": round(float(val), 4)}
        for feat, val in shap_breakdown
    ]

    return score_100, shap_list

@app.get("/")
def health():
    return {
        "status": "Saasify ML API running",
        "models_loaded": True,
        "corpus_size": len(df),
        "model_metrics": model_metrics
    }

@app.post("/analyze")
async def analyze_idea(request: IdeaRequest):
    if len(request.idea.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Idea too short. Please provide at least 10 characters."
        )

    if len(request.idea) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Idea too long. Please keep it under 1000 characters."
        )

    try:
        print(f"\nAnalyzing idea: {request.idea[:50]}...")

        print("Step 1: Finding similar products...")
        similar_products = get_similar_products(request.idea, top_k=8)

        print("Step 2: Running gap analysis...")
        gap_result = {
            "gaps": [],
            "opportunities": [
                "Market is crowded — focus on a specific niche",
                "Consider B2B angle — most competitors target consumers",
                "Focus on workflow integration — competitors are standalone tools"
            ],
            "crowding_level": "High" if len(similar_products) >= 6 else "Medium" if len(similar_products) >= 3 else "Low",
            "competitor_topics": [p["name"] for p in similar_products]
        }      
        print("Step 3: Computing viability score...")
        features = compute_features_for_idea(
            request.idea,
            similar_products
        )
        viability_score, shap_breakdown = compute_viability(features)

        print("Step 4: Generating LLM report...")
        shap_tuples = [
            (item["feature"], item["value"])
            for item in shap_breakdown
        ]
        llm_result = analyze_idea_with_llm(
            request.idea,
            similar_products[:5],
            gap_result,
            viability_score,
            shap_tuples
        )

        return {
            "success": True,
            "idea": request.idea,
            "idea_info": llm_result["idea_info"],
            "similar_products": similar_products[:5],
            "gap_analysis": {
                "gaps": gap_result.get("gaps", []),
                "opportunities": gap_result.get("opportunities", []),
                "crowding_level": gap_result.get("crowding_level", "Medium"),
                "competitor_topics": gap_result.get(
                    "competitor_topics", []
                )[:8]
            },
            "viability": {
                "score": viability_score,
                "features": features,
                "shap_breakdown": shap_breakdown[:5]
            },
            "report": llm_result["report"]
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def save_feedback(request: FeedbackRequest):
    feedback = {
        "idea": request.idea,
        "score": request.score,
        "helpful": request.helpful,
        "comment": request.comment
    }
    os.makedirs("data", exist_ok=True)
    feedback_file = "data/feedback.jsonl"
    with open(feedback_file, "a") as f:
        f.write(json.dumps(feedback) + "\n")
    return {"success": True, "message": "Feedback saved"}

@app.get("/metrics")
def get_metrics():
    return model_metrics

@app.get("/corpus-stats")
def corpus_stats():
    return {
        "total_products": len(df),
        "columns": df.columns.tolist(),
        "sample": df[["name", "tagline"]].head(5).to_dict(orient="records")
    }