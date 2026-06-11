import os
import json

from groq import Groq
from dotenv import load_dotenv

from services.gap_analysis_service import (
    analyze_market_gap
)

from services.competitor_service import (
    find_competitors
)

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)


def generate_recommendations(
    idea,
    competitors=None,
    gap_analysis=None,
    idea_meta=None
):

    if competitors is None:

        competitors = find_competitors(
            idea,
            idea_meta=idea_meta
        )

    if gap_analysis is None:

        gap_analysis = analyze_market_gap(
            idea,
            competitors,
            idea_meta
        )

    prompt = f"""
You are an expert startup advisor.

Startup Idea:

{idea}

Market Analysis:

{json.dumps(gap_analysis)}

Competitors:

{json.dumps(competitors)}

Return ONLY valid JSON.

Format:

{{
  "positioning": [],
  "feature_suggestions": [],
  "customer_segments": [],
  "monetization": []
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
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

    return json.loads(content)