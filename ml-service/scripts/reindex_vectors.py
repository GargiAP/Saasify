import sys
import os

# Fix imports when running from scripts folder
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from database.startup_repository import get_all_startups
from database.vector_repository import save_vector
from services.embedder import generate_embedding


def reindex():

    response = get_all_startups()

    startups = response.data

    print(
        f"Found {len(startups)} startups"
    )

    success_count = 0
    failed_count = 0

    for startup in startups:

        try:

            text = f"""
            Name:
            {startup.get('name', '')}

            Description:
            {startup.get('description', '')}

            Industry:
            {startup.get('industry', '')}

            Subcategory:
            {startup.get('subcategory', '')}

            Target Customer:
            {startup.get('target_customer', '')}

            Business Model:
            {startup.get('business_model', '')}

            Pain Point:
            {startup.get('pain_point', '')}

            Solution:
            {startup.get('solution', '')}
            """

            vector = generate_embedding(text)

            payload = {

                "name":
                    startup.get(
                        "name",
                        ""
                    ),

                "industry":
                    startup.get(
                        "industry",
                        ""
                    ),

                "subcategory":
                    startup.get(
                        "subcategory",
                        ""
                    ),

                "target_customer":
                    startup.get(
                        "target_customer",
                        ""
                    ),

                "business_model":
                    startup.get(
                        "business_model",
                        ""
                    ),

                "pain_point":
                    startup.get(
                        "pain_point",
                        ""
                    ),

                "solution":
                    startup.get(
                        "solution",
                        ""
                    )
            }

            save_vector(
                startup["id"],
                vector,
                payload
            )

            success_count += 1

            print(
                f"Indexed: "
                f"{startup['name']}"
            )

        except Exception as e:

            failed_count += 1

            print(
                f"Failed: "
                f"{startup.get('name', 'Unknown')}"
            )

            print(e)

    print("\n==========")

    print(
        f"Success: {success_count}"
    )

    print(
        f"Failed: {failed_count}"
    )


if __name__ == "__main__":

    reindex()