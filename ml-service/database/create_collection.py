from qdrant_client.models import (
    Distance,
    VectorParams
)

from qdrant_db import client

client.recreate_collection(
    collection_name="startups",
    vectors_config=VectorParams(
        size=384,
        distance=Distance.COSINE
    )
)

print("Collection created")