# training/generate_dataset.py

import pandas as pd
import random

rows = []

for _ in range(3000):

    competitor_count = random.randint(0, 20)

    avg_similarity = round(
        random.uniform(0, 1),
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

    saturation = random.randint(
        1,
        3
    )

    score = (
        100
        - competitor_count * 2
        - avg_similarity * 20
        + opportunity_count * 4
        - risk_count * 2
        - saturation * 5
    )

    score = max(
        0,
        min(
            100,
            score
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

        "saturation":
            saturation,

        "target":
            score
    })

df = pd.DataFrame(rows)

df.to_csv(
    "training_data.csv",
    index=False
)

print(df.head())