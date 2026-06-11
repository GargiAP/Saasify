import json
import joblib
import os

from groq import Groq
from dotenv import load_dotenv

from database.startup_repository import (
    get_all_startups
)

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

cluster_data = joblib.load(
    "models/cluster_data.pkl"
)

response = get_all_startups()

startups = response.data

startup_map = {

    startup["id"]: startup

    for startup in startups
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

cluster_metadata = {}

for cluster_id, startup_ids in clusters.items():

    examples = []

    for startup_id in startup_ids[:10]:

        startup = startup_map.get(
            startup_id
        )

        if startup:

            examples.append(

                startup.get(
                    "name",
                    ""
                )
            )

    prompt = f"""
You are a startup analyst.

These startup names belong
to the same market cluster.

Names:

{examples}

Return ONLY JSON.

Format:

{{
    "segment":""
}}
"""

    response = (
        client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role":"user",
                    "content":prompt
                }
            ],

            temperature=0
        )
    )

    content = (

        response
        .choices[0]
        .message
        .content
        .replace(
            "```json",
            ""
        )
        .replace(
            "```",
            ""
        )
        .strip()
    )

    try:

        result = json.loads(
            content
        )

        cluster_metadata[
            str(cluster_id)
        ] = result

        print(
            cluster_id,
            result
        )

    except:

        cluster_metadata[
            str(cluster_id)
        ] = {

            "segment":
            f"Cluster {cluster_id}"
        }

with open(

    "models/cluster_metadata.json",

    "w",

    encoding="utf-8"
) as f:

    json.dump(

        cluster_metadata,

        f,

        indent=4
    )

print(
    "\nMetadata Saved"
)