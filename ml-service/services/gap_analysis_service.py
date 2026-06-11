import os
import json

from groq import Groq
from dotenv import load_dotenv

from services.competitor_service import (
    find_competitors
)

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)


def analyze_market_gap(
    idea,
    competitors=None,
    idea_meta=None
):

    if competitors is None:

        competitors = find_competitors(
            idea,
            idea_meta=idea_meta
        )

    competitor_text = ""

    for competitor in competitors:

        competitor_text += f"""

Name:
{competitor['name']}

Industry:
{competitor['industry']}

Target Customer:
{competitor['target_customer']}

Business Model:
{competitor['business_model']}

Pain Point:
{competitor['pain_point']}

Solution:
{competitor['solution']}
"""

    prompt = f"""
You are a startup analyst.

Analyze this startup idea against competitors.

Return ONLY valid JSON.

Format:

{{
  "market_saturation":"",
  "opportunities":[],
  "missing_features":[],
  "risks":[],
  "threats":[]
}}

Note for "threats": Do NOT list competitor names as threats. Instead, generate 3-5 actual market threats (e.g. platform dependency, AI commoditization, rising acquisition costs, regulation, retention challenges) relevant to this startup idea.

IDEA:

{idea}

COMPETITORS:

{competitor_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1:
        content = content[start:end + 1]

    res = json.loads(content)
    if "threats" not in res or not isinstance(res["threats"], list):
        res["threats"] = []
    return res