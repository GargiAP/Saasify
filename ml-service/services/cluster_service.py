import json
import joblib
import hdbscan
import numpy as np

from services.embedder import (
    generate_embedding
)

from database.startup_repository import (
    get_all_startups
)

umap_model = joblib.load(
    "models/umap_model.pkl"
)

cluster_model = joblib.load(
    "models/hdbscan_model.pkl"
)

cluster_data = joblib.load(
    "models/cluster_data.pkl"
)

with open(

    "models/cluster_metadata.json",

    "r",

    encoding="utf-8"
) as f:

    cluster_metadata = (
        json.load(f)
    )

response = get_all_startups()

startups = response.data

startup_map = {

    startup["id"]: startup

    for startup in startups
}

cluster_counts = {}

for row in cluster_data:

    cluster_id = row["cluster_id"]

    if cluster_id == -1:
        continue

    cluster_counts[
        cluster_id
    ] = (

        cluster_counts.get(
            cluster_id,
            0
        )
        + 1
    )


def find_cluster(
    idea
):

    embedding = np.array([
        generate_embedding(
            idea
        )
    ])

    reduced = (
        umap_model.transform(
            embedding
        )
    )

    probabilities = (

        hdbscan.prediction
        .membership_vector(

            cluster_model,
            reduced
        )
    )

    cluster_id = int(

        np.argmax(
            probabilities[0]
        )
    )

    confidence = float(

        np.max(
            probabilities[0]
        )
    )

    return {

        "cluster_id":
            cluster_id,

        "confidence":
            round(
                confidence * 100,
                2
            ),

        "reduced_vector":
            reduced[0]
    }


def get_cluster_startups(
    cluster_id
):

    startup_ids = [

        row["startup_id"]

        for row in cluster_data

        if row["cluster_id"]
        == cluster_id
    ]

    return [

        startup_map[sid]

        for sid in startup_ids

        if sid in startup_map
    ]


def competition_score(
    cluster_size
):

    score = min(
        100,
        cluster_size * 4
    )

    return round(
        score,
        2
    )


def differentiation_score(
    competitors
):

    if not competitors:

        return 100

    top_scores = [

        c["score"]

        for c in competitors[:5]
    ]

    avg_similarity = (
        sum(top_scores)
        /
        len(top_scores)
    )

    score = max(
        0,
        100 - avg_similarity
    )

    return round(
        score,
        2
    )

def analyze_cluster(
    idea,
    idea_meta=None
):

    result = (
        find_cluster(
            idea
        )
    )

    cluster_id = (
        result["cluster_id"]
    )

    confidence = (
        result["confidence"]
    )

    startups = (
        get_cluster_startups(
            cluster_id
        )
    )

    cluster_size = len(
        startups
    )

    competition = (
        competition_score(
            cluster_size
        )
    )

    from services.competitor_service import (
        find_competitors
    )

    competitors = (
            find_competitors(
                idea
            )
        )

    differentiation = (
            differentiation_score(
                competitors
            )
        )

    if competition >= 80:

       level = "High"

    elif competition >= 50:

        level = "Medium"

    else:

        level = "Low"

    segment = (

        cluster_metadata.get(

            str(cluster_id),

            {}
        )

        .get(
            "segment",
            f"Cluster {cluster_id}"
        )
    )

    if (confidence < 50.0 or cluster_id == -1) and idea_meta:
        segment = idea_meta.get("subcategory") or idea_meta.get("industry") or segment

    return {

        "market_segment":
            segment,

        "cluster_id":
            cluster_id,

        "cluster_size":
            cluster_size,

        "confidence":
            confidence,

        "competition_score":
            round(
                competition,
                2
            ),

        "competition_level":
            level,

        "differentiation_score":
            differentiation,

        "sample_startups":[

            startup.get(
                "name",
                ""
            )

            for startup in startups[:5]
        ]
    }