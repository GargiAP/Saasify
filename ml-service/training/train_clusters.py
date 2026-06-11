import joblib
import numpy as np

from database.startup_repository import (
    get_all_startups
)

from services.embedder import (
    generate_embedding
)

import umap
import hdbscan


print(
    "Loading startups..."
)

response = get_all_startups()

startups = response.data

print(
    f"Found {len(startups)} startups"
)

# -----------------------
# Build embeddings
# -----------------------

embeddings = []

startup_ids = []

for startup in startups:

    text = f"""
    Name:
    {startup.get('name','')}

    Description:
    {startup.get('description','')}

    Industry:
    {startup.get('industry','')}

    Subcategory:
    {startup.get('subcategory','')}

    Pain Point:
    {startup.get('pain_point','')}

    Solution:
    {startup.get('solution','')}
    """

    vector = generate_embedding(
        text
    )

    embeddings.append(
        vector
    )

    startup_ids.append(
        startup["id"]
    )

embeddings = np.array(
    embeddings
)

print(
    "Embeddings ready"
)

# -----------------------
# UMAP
# -----------------------

print(
    "Running UMAP..."
)

reducer = umap.UMAP(
    n_neighbors=15,
    n_components=20,
    metric="cosine",
    random_state=42
)

reduced_vectors = (
    reducer.fit_transform(
        embeddings
    )
)

print(
    "UMAP completed"
)

# -----------------------
# HDBSCAN
# -----------------------

print(
    "Running HDBSCAN..."
)

clusterer = hdbscan.HDBSCAN(
    min_cluster_size=8,
    min_samples=2,
    prediction_data=True
)

labels = clusterer.fit_predict(
    reduced_vectors
)

print(
    "Clustering completed"
)

unique_clusters = len(
    set(labels)
)

print(
    f"Clusters Found: "
    f"{unique_clusters}"
)

cluster_data = []

for startup_id, label in zip(
    startup_ids,
    labels
):

    cluster_data.append({

        "startup_id":
            startup_id,

        "cluster_id":
            int(label)
    })

joblib.dump(
    reducer,
    "models/umap_model.pkl"
)

joblib.dump(
    clusterer,
    "models/hdbscan_model.pkl"
)

joblib.dump(
    cluster_data,
    "models/cluster_data.pkl"
)

print(
    "Models Saved"
)