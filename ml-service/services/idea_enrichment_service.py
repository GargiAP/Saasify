import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)


def enrich_idea(
    idea
):

    prompt = f"""
Analyze this startup idea.

Return ONLY valid JSON.

Do not explain anything.

Format:

{{
    "industry":"",
    "subcategory":"",
    "target_customer":"",
    "business_model":"",
    "pain_point":"",
    "solution":""
}}

Idea:

{idea}
"""

    response = (
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1
        )
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    content = (
        content
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

    start = content.find("{")
    end = content.rfind("}")

    if (
        start != -1
        and
        end != -1
    ):
        content = (
            content[
                start:end + 1
            ]
        )

    data = json.loads(
        content
    )

    return {

        "industry":
            data.get(
                "industry",
                ""
            ),

        "subcategory":
            data.get(
                "subcategory",
                ""
            ),

        "target_customer":
            data.get(
                "target_customer",
                ""
            ),

        "business_model":
            data.get(
                "business_model",
                ""
            ),

        "pain_point":
            data.get(
                "pain_point",
                ""
            ),

        "solution":
            data.get(
                "solution",
                ""
            )
    }