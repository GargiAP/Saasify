import requests
import time
import os
from dotenv import load_dotenv
from services.startup_ingestion import ingest_startup

load_dotenv()

CLIENT_ID = os.getenv("PRODUCTHUNT_CLIENT_ID")
CLIENT_SECRET = os.getenv("PRODUCTHUNT_CLIENT_SECRET")
CURSOR_FILE = "data/last_cursor.txt"


def get_access_token():

    response = requests.post(
        "https://api.producthunt.com/v2/oauth/token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )

    response.raise_for_status()

    return response.json()["access_token"]


def fetch_products(token, cursor=None):

    after = f', after: "{cursor}"' if cursor else ""

    query = f"""
    {{
      posts(first: 50{after}) {{
        edges {{
          node {{
            name
            tagline
            description
            votesCount
            createdAt
            topics {{
              edges {{
                node {{
                  name
                }}
              }}
            }}
          }}
        }}
        pageInfo {{
          hasNextPage
          endCursor
        }}
      }}
    }}
    """

    while True:

        response = requests.post(
            "https://api.producthunt.com/v2/api/graphql",
            json={"query": query},
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        if response.status_code == 429:

            print(
                "\nRate limit hit. Sleeping for 60 seconds..."
            )

            time.sleep(60)

            continue

        response.raise_for_status()

        return response.json()


def scrape_products(target=20):

    print("Getting Product Hunt access token...")

    token = get_access_token()

    cursor = load_cursor()

    processed = 0

    while processed < target:

        print(
            f"Processed {processed}/{target}"
        )

        data = fetch_products(
            token,
            cursor
        )

        posts = data["data"]["posts"]

        edges = posts["edges"]

        for edge in edges:

            if processed >= target:
                break

            node = edge["node"]

            topics = [
                t["node"]["name"]
                for t in node["topics"]["edges"]
            ]

            startup = {

                "name":
                    node["name"],

                "description":
                    f"{node['tagline']} "
                    f"{node['description']}",

                "industry":
                    "",

                "subcategory":
                    "",

                "target_customer":
                    "",

                "business_model":
                    "",

                "pain_point":
                    "",

                "solution":
                    "",

                "website":
                    "",

                "source":
                    "producthunt",

                "tags":
                    topics
            }

            try:

                ingest_startup(
                    startup
                )

                processed += 1

            except Exception as e:

                print(
                    f"Failed: "
                    f"{startup['name']}"
                )

                print(e)

        if not posts["pageInfo"]["hasNextPage"]:

            print(
                "No more Product Hunt pages."
            )

            break

        cursor = (
            posts["pageInfo"]
            ["endCursor"]
        )
        save_cursor(cursor)
        time.sleep(3)

    print(
        f"\nFinished. "
        f"Inserted {processed} startups."
    )

def save_cursor(cursor):

    os.makedirs(
        "data",
        exist_ok=True
    )

    with open(
        CURSOR_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(cursor)


def load_cursor():

    if not os.path.exists(
        CURSOR_FILE
    ):
        return None

    with open(
        CURSOR_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return f.read().strip()
    
if __name__ == "__main__":

    print("Starting Product Hunt ingestion...\n")

    scrape_products(
        target=1000
    )