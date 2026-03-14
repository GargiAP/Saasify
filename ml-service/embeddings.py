import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import os

def build_index():
    print("Loading products...")
    df = pd.read_csv("data/products.csv")
    
    # combine name + tagline + description into one text per product
    df["combined_text"] = (
        df["name"].fillna("") + " " +
        df["tagline"].fillna("") + " " +
        df["description"].fillna("")
    )

    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Generating embeddings for all products...")
    embeddings = model.encode(
        df["combined_text"].tolist(),
        show_progress_bar=True,
        batch_size=32
    )

    embeddings = np.array(embeddings).astype("float32")
    print(f"Embeddings shape: {embeddings.shape}")

    # normalize for cosine similarity
    faiss.normalize_L2(embeddings)

    # build FAISS index
    print("Building FAISS index...")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    print(f"Index built with {index.ntotal} vectors")

    # save everything
    os.makedirs("models", exist_ok=True)
    faiss.write_index(index, "models/products.index")
    df.to_csv("data/products_clean.csv", index=False)
    
    with open("models/embeddings.pkl", "wb") as f:
        pickle.dump(embeddings, f)

    print("Saved index to models/products.index")
    print("Done!")
    return index, df, embeddings

def search_similar(query, index, df, model, top_k=5):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype("float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        results.append({
            "name": df.iloc[idx]["name"],
            "tagline": df.iloc[idx]["tagline"],
            "similarity": round(float(score), 3)
        })
    return results

if __name__ == "__main__":
    index, df, embeddings = build_index()

    # test it with a sample idea
    print("\nTesting similarity search...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    test_idea = "an app that helps content creators find viral video ideas using AI"
    results = search_similar(test_idea, index, df, model)
    
    print(f"\nTop 5 similar products for: '{test_idea}'")
    for r in results:
        print(f"  {r['name']} — {r['tagline']} (similarity: {r['similarity']})")