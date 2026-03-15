import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_competition_density(idx, embeddings, top_k=10):
    query = embeddings[idx].reshape(1, -1).astype("float32")
    faiss.normalize_L2(query)
    temp_index = faiss.IndexFlatIP(embeddings.shape[1])
    norm_embeddings = embeddings.copy().astype("float32")
    faiss.normalize_L2(norm_embeddings)
    temp_index.add(norm_embeddings)
    scores, _ = temp_index.search(query, top_k + 1)
    return float(np.mean(scores[0][1:]))

def compute_market_growth(topics_str):
    high_growth = [
        "ai", "artificial intelligence", "machine learning",
        "automation", "no-code", "nocode", "productivity",
        "developer tools", "api", "saas", "analytics",
        "collaboration", "remote", "security", "data",
        "crypto", "web3", "blockchain", "fintech", "health"
    ]
    if not isinstance(topics_str, str):
        return 0.2
    t = topics_str.lower()
    matches = sum(1 for w in high_growth if w in t)
    return min(1.0, matches * 0.12 + 0.2)

def compute_pain_severity(description):
    pain_words = [
        "frustrat", "difficult", "hard to", "struggle",
        "problem", "issue", "challenge", "slow", "manual",
        "expensive", "time-consuming", "complex", "confus",
        "broken", "inefficient", "annoying", "tedious",
        "waste", "miss", "fail", "error", "bug", "crash",
        "impossible", "painful", "nightmare", "hate"
    ]
    if not isinstance(description, str):
        return 0.2
    d = description.lower()
    matches = sum(1 for w in pain_words if w in d)
    return min(1.0, matches * 0.12 + 0.2)

def compute_monetization_signal(description, topics_str):
    monetization_words = [
        "subscription", "pricing", "enterprise", "pro plan",
        "freemium", "api access", "saas", "b2b", "revenue",
        "billing", "payment", "premium", "business", "team",
        "invoice", "checkout", "stripe", "per month", "per year",
        "license", "seats", "users", "clients", "customers"
    ]
    text = (str(description) + " " + str(topics_str)).lower()
    matches = sum(1 for w in monetization_words if w in text)
    return min(1.0, matches * 0.10 + 0.2)

def compute_description_quality(name, tagline, description):
    score = 0.0
    
    # length signal — longer = more thought out
    desc = str(description) if isinstance(description, str) else ""
    tag = str(tagline) if isinstance(tagline, str) else ""
    
    if len(desc) > 300:
        score += 0.3
    elif len(desc) > 100:
        score += 0.15
    
    if len(tag) > 30:
        score += 0.2
    
    # specificity signal — numbers and specific claims
    import re
    numbers = re.findall(r'\d+', desc + tag)
    if len(numbers) >= 2:
        score += 0.2
    
    # action words — strong value propositions
    action_words = [
        "save", "increase", "reduce", "automate", "generate",
        "track", "manage", "build", "create", "analyze",
        "optimize", "improve", "discover", "launch", "scale"
    ]
    matches = sum(1 for w in action_words if w in (desc + tag).lower())
    score += min(0.3, matches * 0.06)
    
    return min(1.0, score)

def compute_novelty_score(idx, embeddings, top_k=5):
    query = embeddings[idx].reshape(1, -1).astype("float32")
    faiss.normalize_L2(query)
    temp_index = faiss.IndexFlatIP(embeddings.shape[1])
    norm_embeddings = embeddings.copy().astype("float32")
    faiss.normalize_L2(norm_embeddings)
    temp_index.add(norm_embeddings)
    scores, _ = temp_index.search(query, top_k + 1)
    avg_similarity = float(np.mean(scores[0][1:]))
    # novelty = inverse of similarity
    return round(1.0 - avg_similarity, 4)

def compute_topic_diversity(topics_str):
    if not isinstance(topics_str, str):
        return 0.2
    topics = [t.strip() for t in topics_str.split(",") if t.strip()]
    # more diverse topics = broader appeal
    return min(1.0, len(topics) * 0.15 + 0.1)

def build_training_data():
    print("Loading data...")
    df = pd.read_csv("data/products_clean.csv")
    
    print("Loading embeddings...")
    with open("models/embeddings.pkl", "rb") as f:
        embeddings = pickle.load(f)
    
    print("Computing features...")
    features = []
    
    for idx, row in df.iterrows():
        if idx % 50 == 0:
            print(f"  Processing {idx}/{len(df)}...")
        
        features.append({
            "name": row["name"],
            "competition_density": compute_competition_density(
                idx, embeddings
            ),
            "novelty_score": compute_novelty_score(idx, embeddings),
            "market_growth": compute_market_growth(
                row.get("topics", "")
            ),
            "pain_severity": compute_pain_severity(
                row.get("description", "")
            ),
            "monetization_signal": compute_monetization_signal(
                row.get("description", ""),
                row.get("topics", "")
            ),
            "description_quality": compute_description_quality(
                row.get("name", ""),
                row.get("tagline", ""),
                row.get("description", "")
            ),
            "topic_diversity": compute_topic_diversity(
                row.get("topics", "")
            ),
            "votes": row.get("votes", 0)
        })
    
    features_df = pd.DataFrame(features)
    
    print("\nCreating labels...")
    features_df["label"] = 0
    features_df.loc[features_df["votes"] > 0, "label"] = 1
    
    pos = features_df["label"].sum()
    neg = len(features_df) - pos
    print(f"Positive: {pos} | Negative: {neg}")
    
    if pos > len(features_df) * 0.5:
        threshold = features_df[
            features_df["votes"] > 0
        ]["votes"].median()
        features_df["label"] = 0
        features_df.loc[features_df["votes"] >= threshold, "label"] = 1
        print(f"Adjusted threshold: votes >= {threshold}")
    
    print(f"\nFinal distribution:")
    print(features_df["label"].value_counts())
    print(f"Success rate: {features_df['label'].mean():.1%}")
    
    os.makedirs("data", exist_ok=True)
    features_df.to_csv("data/training_data.csv", index=False)
    print(f"\nSaved to data/training_data.csv")
    return features_df

if __name__ == "__main__":
    df = build_training_data()
    print("\nFeature statistics:")
    cols = [
        "competition_density", "novelty_score", "market_growth",
        "pain_severity", "monetization_signal",
        "description_quality", "topic_diversity"
    ]
    print(df[cols].describe().round(3))