import joblib
from collections import Counter

cluster_data = joblib.load(
    "models/cluster_data.pkl"
)

labels = [

    row["cluster_id"]

    for row in cluster_data
]

counts = Counter(
    labels
)

print("\nCluster Sizes\n")

for cluster_id, size in sorted(
    counts.items(),
    key=lambda x: x[1],
    reverse=True
):

    print(
        f"Cluster {cluster_id}: "
        f"{size}"
    )