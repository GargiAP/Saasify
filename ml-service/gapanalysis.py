import pandas as pd
import numpy as np
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer
from collections import Counter
import faiss
import pickle

sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
kw_model = KeyBERT(model=sentence_model)

def extract_keywords(text, top_n=5):
    # clean text to remove product names (usually first word/capitalized)
    import re
    text = re.sub(r'\b[A-Z][a-z]*[A-Z][a-z]*\b', '', text)  # remove CamelCase words
    text = re.sub(r'\s+', ' ', text).strip()
    
    keywords = kw_model.extract_keywords(
        text,
        keyphrase_ngram_range=(1, 2),
        stop_words="english",
        use_mmr=True,       
        diversity=0.5,
        top_n=top_n
    )
    return [kw[0] for kw in keywords if len(kw[0]) > 3]

def get_crowding_level(num_similar):
    if num_similar >= 6:
        return "High"
    elif num_similar >= 3:
        return "Medium"
    else:
        return "Low"

def analyze_gaps(user_idea, df, index, top_k=8):
    print("\nStep 1: Extracting keywords from your idea...")
    idea_keywords = extract_keywords(user_idea, top_n=8)
    print(f"Your idea is about: {idea_keywords}")

    print("\nStep 2: Finding similar products...")
    idea_embedding = sentence_model.encode([user_idea])
    idea_embedding = np.array(idea_embedding).astype("float32")
    faiss.normalize_L2(idea_embedding)
    scores, indices = index.search(idea_embedding, top_k)

    similar_products = []
    for score, idx in zip(scores[0], indices[0]):
        similar_products.append({
            "name": df.iloc[idx]["name"],
            "tagline": df.iloc[idx]["tagline"],
            "combined_text": df.iloc[idx]["combined_text"],
            "similarity": round(float(score), 3)
        })
    
    print(f"Found {len(similar_products)} similar products")

    print("\nStep 3: Extracting keywords from competitors...")
    competitor_keywords = []
    for product in similar_products:
        text = str(product["combined_text"])
        if text.strip():
            kws = extract_keywords(text, top_n=5)
            competitor_keywords.extend(kws)

    keyword_freq = Counter(competitor_keywords)
    top_competitor_topics = [kw for kw, _ in keyword_freq.most_common(15)]
    print(f"Competitors focus on: {top_competitor_topics}")

    print("\nStep 4: Finding gaps...")
    gaps = []
    for idea_kw in idea_keywords:
        idea_kw_emb = sentence_model.encode([idea_kw])
        
        is_covered = False
        for comp_kw in top_competitor_topics:
            comp_kw_emb = sentence_model.encode([comp_kw])
            
            dot = float(np.dot(idea_kw_emb.flatten(), comp_kw_emb.flatten()))
            norm = float(np.linalg.norm(idea_kw_emb) * np.linalg.norm(comp_kw_emb))
            similarity = dot / norm     

            if similarity > 0.65:
                is_covered = True
                break
        
        if not is_covered:
            gaps.append(idea_kw)

    print(f"Gaps found: {gaps}")

    opportunities = []
    for gap in gaps[:3]:
        opportunities.append(f"Build around '{gap}' — competitors are not focusing here")
    
    crowding = get_crowding_level(len(similar_products))
    if crowding == "High":
        opportunities.append("Market is crowded — you need a very specific niche to stand out")
    elif crowding == "Medium":
        opportunities.append("Market has some players — differentiation is important")
    else:
        opportunities.append("Low competition — first mover advantage possible")

    return {
        "similar_products": similar_products,
        "idea_keywords": idea_keywords,
        "competitor_topics": top_competitor_topics,
        "gaps": gaps,
        "opportunities": opportunities,
        "crowding_level": crowding
    }

if __name__ == "__main__":
    print("Loading data and index...")
    df = pd.read_csv("data/products_clean.csv")
    index = faiss.read_index("models/products.index")

    test_idea = "an app that helps content creators find viral video ideas using AI"
    
    print(f"\nAnalyzing idea: '{test_idea}'")
    result = analyze_gaps(test_idea, df, index)

    print("\n========== FINAL GAP ANALYSIS ==========")
    print(f"\nCrowding level: {result['crowding_level']}")
    print(f"\nYour idea keywords:  {result['idea_keywords']}")
    print(f"\nCompetitors focus on: {result['competitor_topics']}")
    print(f"\nGaps detected: {result['gaps']}")
    print(f"\nOpportunity directions:")
    for opp in result['opportunities']:
        print(f"  -> {opp}")
    print(f"\nTop similar products:")
    for p in result['similar_products'][:5]:
        print(f"  {p['name']} — {p['tagline']} ({p['similarity']})")