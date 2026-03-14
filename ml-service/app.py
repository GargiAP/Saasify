from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import numpy as np

app = FastAPI()

model = SentenceTransformer("all-MiniLM-L6-v2")

class IdeaRequest(BaseModel):
    idea: str


categories = {
    "Creator Tools": "software tools for content creators on YouTube TikTok Instagram",
    "Developer Tools": "tools that help developers build and deploy software",
    "Marketing Tools": "software used for marketing campaigns analytics SEO",
    "Productivity Tools": "applications that improve personal or team productivity",
    "AI Tools": "applications powered by artificial intelligence"
}


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


@app.get("/")
def health():
    return {"status": "ML service running"}


@app.post("/market-category")
def detect_market_category(request: IdeaRequest):

    idea_embedding = model.encode(request.idea)

    best_category = None
    best_score = -1

    for name, desc in categories.items():

        category_embedding = model.encode(desc)

        similarity = cosine_similarity(
            idea_embedding,
            category_embedding
        )

        if similarity > best_score:
            best_score = similarity
            best_category = name

    return {
        "category": best_category,
        "similarity": float(best_score)
    }