from services.embedder import generate_embedding
from database.qdrant_db import client

def search_similar(text):

    vector = generate_embedding(text)

    results = client.query_points(
        collection_name="startups",
        query=vector,
        limit=5
    )

    return results