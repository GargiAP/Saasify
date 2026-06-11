import random
import pandas as pd

rows = []

for _ in range(5000):

    competitor_count = random.randint(
        0,
        20
    )

    avg_similarity = round(
        random.uniform(
            0.1,
            1.0
        ),
        3
    )

    opportunity_count = random.randint(
        0,
        10
    )

    risk_count = random.randint(
        0,
        10
    )

    missing_feature_count = random.randint(
        0,
        10
    )

    score = (

        100

        - competitor_count * 2

        - avg_similarity * 25

        - risk_count * 4

        + opportunity_count * 6

        + missing_feature_count * 2

    )

    score = max(
        0,
        min(
            score,
            100
        )
    )

    rows.append({

        "competitor_count":
            competitor_count,

        "avg_similarity":
            avg_similarity,

        "opportunity_count":
            opportunity_count,

        "risk_count":
            risk_count,

        "missing_feature_count":
            missing_feature_count,

        "target_score":
            round(
                score,
                2
            )
    })

df = pd.DataFrame(
    rows
)

print(
    df.head()
)

df.to_csv(
    "opportunity_dataset.csv",
    index=False
)

print(
    "\nDataset Generated"
)