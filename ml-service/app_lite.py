from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
import json
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Saasify ML API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

print("Loading models...")

df = pd.read_csv("data/products_clean.csv")

with open("models/viability_model.pkl", "rb") as f:
    viability_model = pickle.load(f)

with open("models/shap_explainer.pkl", "rb") as f:
    shap_explainer = pickle.load(f)

with open("models/feature_cols.pkl", "rb") as f:
    feature_cols = pickle.load(f)

with open("models/metrics.json", "r") as f:
    model_metrics = json.load(f)

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print(f"Loaded {len(df)} products. All models ready!")


class IdeaRequest(BaseModel):
    idea: str


def get_similar_products(idea: str, top_k: int = 8):
    idea_words = set(idea.lower().split())
    scores = []
    for _, row in df.iterrows():
        text = str(row.get("combined_text", "")).lower()
        text_words = set(text.split())
        overlap = len(idea_words & text_words)
        score = overlap / (len(idea_words) + 1)
        scores.append(score)

    scores = np.array(scores)
    top_indices = np.argsort(scores)[::-1][:top_k]
    top_scores = scores[top_indices]
    max_score = top_scores.max() if top_scores.max() > 0 else 1
    top_scores = (top_scores / max_score) * 0.6

    results = []
    for score, idx in zip(top_scores, top_indices):
        results.append({
            "name": str(df.iloc[idx]["name"]),
            "tagline": str(df.iloc[idx]["tagline"]),
            "similarity": round(float(score), 3)
        })
    return results


def compute_features(idea: str, similar_products: list):
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
        "frustrat", "difficult", "hard", "struggle",
        "problem", "issue", "slow", "manual",
        "expensive", "complex", "broken", "inefficient"
    ]
    pain_severity = min(1.0, sum(
        1 for w in pain_words if w in idea_lower
    ) * 0.15 + 0.2)

    monetization_words = [
        "subscription", "enterprise", "b2b", "saas",
        "business", "payment", "premium", "team"
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
    return score_100, [
        {"feature": f, "value": round(float(v), 4)}
        for f, v in shap_breakdown
    ]


def call_llm(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()


def preprocess_idea(idea: str) -> dict:
    prompt = f"""Extract info from this startup idea and return ONLY valid JSON with no extra text:
"{idea}"

Return exactly this structure:
{{
  "cleaned_idea": "one clear sentence",
  "problem_being_solved": "the main pain point",
  "target_audience": "who uses this",
  "core_value_proposition": "main benefit",
  "market_category": "one of: Developer Tools, AI Tools, Marketing Tools, Productivity Tools, Creator Tools, Fintech, Health Tech, E-commerce, Education, Other",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}}"""

    response = call_llm(prompt)
    response = re.sub(r'```json\s*', '', response)
    response = re.sub(r'```\s*', '', response).strip()

    try:
        return json.loads(response)
    except:
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
        return {
            "cleaned_idea": idea,
            "problem_being_solved": "unclear",
            "target_audience": "unclear",
            "core_value_proposition": "unclear",
            "market_category": "Other",
            "keywords": []
        }


def generate_report(
    idea_info: dict,
    similar_products: list,
    gap_analysis: dict,
    viability_score: int,
    shap_breakdown: list
) -> str:
    competitors = "\n".join([
        f"- {p['name']}: {p['tagline']}"
        for p in similar_products[:4]
    ])
    shap_text = "\n".join([
        f"- {s['feature'].replace('_', ' ')}: {'helps' if s['value'] > 0 else 'hurts'} ({s['value']:+.3f})"
        for s in shap_breakdown[:4]
    ])

    prompt = f"""You are Saasify, an expert startup analyst. Write a concise analysis report.

Idea: {idea_info.get('cleaned_idea')}
Problem: {idea_info.get('problem_being_solved')}
Target: {idea_info.get('target_audience')}
Market: {idea_info.get('market_category')}

Similar competitors:
{competitors}

Viability score: {viability_score}/100
Score factors:
{shap_text}

Market crowding: {gap_analysis.get('crowding_level')}

Write exactly these sections:
1. IDEA SUMMARY (2 sentences)
2. MARKET LANDSCAPE (2-3 sentences)
3. KEY GAPS AND OPPORTUNITIES (3 bullet points)
4. VIABILITY ASSESSMENT (2 sentences explaining the score)
5. WHAT TO VALIDATE NEXT (3 specific actionable steps)

Be direct and honest. Talk like a senior investor."""

    return call_llm(prompt)


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
            detail="Idea too short"
        )

    try:
        print(f"Analyzing: {request.idea[:50]}...")

        similar_products = get_similar_products(request.idea, top_k=8)

        gap_result = {
            "gaps": [
                "pre-creation workflow",
                "idea discovery",
                "trend prediction",
                "niche audience targeting"
            ],
            "opportunities": [
                "Market is crowded — focus on a specific niche",
                "Consider B2B angle — most competitors target consumers",
                "Focus on workflow integration — competitors are standalone tools"
            ],
            "crowding_level": "High" if len(similar_products) >= 6 else "Medium" if len(similar_products) >= 3 else "Low",
            "competitor_topics": [p["name"] for p in similar_products]
        }

        features = compute_features(request.idea, similar_products)
        viability_score, shap_breakdown = compute_viability(features)

        idea_info = preprocess_idea(request.idea)
        import time
        time.sleep(1)
        report = generate_report(
            idea_info,
            similar_products,
            gap_result,
            viability_score,
            shap_breakdown
        )

        return {
            "success": True,
            "idea": request.idea,
            "idea_info": idea_info,
            "similar_products": similar_products[:5],
            "gap_analysis": gap_result,
            "viability": {
                "score": viability_score,
                "features": features,
                "shap_breakdown": shap_breakdown[:5]
            },
            "report": report
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
async def save_feedback(request: dict):
    os.makedirs("data", exist_ok=True)
    with open("data/feedback.jsonl", "a") as f:
        f.write(json.dumps(request) + "\n")
    return {"success": True}


@app.get("/metrics")
def get_metrics():
    return model_metrics
