import joblib

from database.startup_repository import (
    get_all_startups
)

cluster_data = joblib.load(
    "models/cluster_data.pkl"
)

response = get_all_startups()

startups = response.data

startup_map = {
    s["id"]: s
    for s in startups
}

clusters = {}

for row in cluster_data:

    cluster_id = row["cluster_id"]

    if cluster_id == -1:
        continue

    clusters.setdefault(
        cluster_id,
        []
    )

    clusters[
        cluster_id
    ].append(
        row["startup_id"]
    )

for cluster_id in sorted(
    clusters.keys()
):

    print(
        f"\n========== "
        f"CLUSTER {cluster_id}"
        f" =========="
    )

    for startup_id in clusters[
        cluster_id
    ][:5]:

        startup = startup_map[
            startup_id
        ]

        print(
            startup.get(
                "name",
                ""
            )
        )