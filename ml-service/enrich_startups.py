from services.enrichment_service import enrich_startup

from database.startup_repository import (
    get_unenriched_startups,
    update_startup
)

import time

BATCH_SIZE = 20


while True:

    startups = get_unenriched_startups(
        limit=BATCH_SIZE
    )

    rows = startups.data

    if len(rows) == 0:

        print(
            "All startups enriched."
        )

        break

    for startup in rows:

        try:

            print(
                f"Processing: {startup['name']}"
            )

            result = enrich_startup(
                startup["name"],
                startup["description"]
            )

            update_startup(
                startup["id"],
                {
                    "industry":
                        result.get(
                            "industry",
                            ""
                        ),

                    "subcategory":
                        result.get(
                            "subcategory",
                            ""
                        ),

                    "target_customer":
                        result.get(
                            "target_customer",
                            ""
                        ),

                    "business_model":
                        result.get(
                            "business_model",
                            ""
                        ),

                    "pain_point":
                        result.get(
                            "pain_point",
                            ""
                        ),

                    "solution":
                        result.get(
                            "solution",
                            ""
                        ),

                    "enriched": True
                }
            )

            print(
                f"Done: {startup['name']}"
            )

            time.sleep(1)

        except Exception as e:

            print(
                f"Failed: {startup['name']}"
            )

            print(e)