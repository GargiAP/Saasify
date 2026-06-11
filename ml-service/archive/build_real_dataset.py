import pandas as pd

from database.startup_repository import (
    get_all_startups
)

rows = []

response = get_all_startups()

for startup in response.data:

    description = (
        startup.get(
            "description",
            ""
        )
    )

    industry_present = int(
        bool(
            startup.get(
                "industry"
            )
        )
    )

    subcategory_present = int(
        bool(
            startup.get(
                "subcategory"
            )
        )
    )

    customer_present = int(
        bool(
            startup.get(
                "target_customer"
            )
        )
    )

    business_model_present = int(
        bool(
            startup.get(
                "business_model"
            )
        )
    )

    pain_point_present = int(
        bool(
            startup.get(
                "pain_point"
            )
        )
    )

    solution_present = int(
        bool(
            startup.get(
                "solution"
            )
        )
    )

    description_length = len(
        description
    )

    score = (

        industry_present * 10
        + subcategory_present * 10
        + customer_present * 15
        + business_model_present * 15
        + pain_point_present * 20
        + solution_present * 20
        + min(
            description_length / 10,
            10
        )
    )

    rows.append({

        "description_length":
            description_length,

        "industry_present":
            industry_present,

        "subcategory_present":
            subcategory_present,

        "customer_present":
            customer_present,

        "business_model_present":
            business_model_present,

        "pain_point_present":
            pain_point_present,

        "solution_present":
            solution_present,

        "target":
            score
    })

df = pd.DataFrame(rows)

df.to_csv(
    "real_training_data.csv",
    index=False
)

print(df.head())