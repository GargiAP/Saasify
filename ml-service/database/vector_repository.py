from qdrant_client.models import PointStruct
from database.qdrant_db import client


def save_vector(
    startup_id,
    vector,
    payload
):

    client.upsert(
        collection_name="startups",
        points=[
            PointStruct(
                id=startup_id,
                vector=vector,
                payload=payload
            )
        ]
    )

    print("Vector saved")