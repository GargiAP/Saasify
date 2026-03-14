import requests
import pandas as pd
import time
import os

CLIENT_ID = "OzsZoo24R0YnTdjQENP-9P5QlAbnGjRbkaWCIUb3vtc"
CLIENT_SECRET = "OPc_k0pwBEbdt100oJ_wfcxaQYvpC1FUhMQv51qvLpk"

def get_access_token():
    response = requests.post(
        "https://api.producthunt.com/v2/oauth/token",
        json={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )
    return response.json()["access_token"]

def fetch_products(token, cursor=None):
    after = f', after: "{cursor}"' if cursor else ''
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
          cursor
        }}
        pageInfo {{
          hasNextPage
          endCursor
        }}
      }}
    }}
    """
    response = requests.post(
        "https://api.producthunt.com/v2/api/graphql",
        json={"query": query},
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json()

def scrape_products(target=500):
    print("Getting access token...")
    token = get_access_token()

    all_products = []
    cursor = None

    while len(all_products) < target:
        print(f"Fetching products... got {len(all_products)} so far")
        data = fetch_products(token, cursor)

        posts = data["data"]["posts"]
        edges = posts["edges"]

        for edge in edges:
            node = edge["node"]
            topics = [t["node"]["name"] for t in node["topics"]["edges"]]

            all_products.append({
                "name": node["name"],
                "tagline": node["tagline"],
                "description": node["description"] or node["tagline"],
                "votes": node["votesCount"],
                "created_at": node["createdAt"],
                "topics": ", ".join(topics)
            })

        if not posts["pageInfo"]["hasNextPage"]:
            print("No more pages available")
            break

        cursor = posts["pageInfo"]["endCursor"]
        time.sleep(1)

    df = pd.DataFrame(all_products)
    df = df.drop_duplicates(subset=["name"])
    df = df.dropna(subset=["description"])

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/products.csv", index=False)
    print(f"Saved {len(df)} products to data/products.csv")
    return df

if __name__ == "__main__":
    df = scrape_products(target=500)
    print(df.head())
    print(f"\nTotal products: {len(df)}")
    print(f"Columns: {df.columns.tolist()}")