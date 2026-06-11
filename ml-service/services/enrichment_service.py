import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def enrich_startup(name, description):

    prompt = f"""
Analyze this startup.

Return ONLY valid JSON.

Do not use markdown.
Do not use code fences.
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

Startup Name:
{name}

Description:
{description}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    content = response.choices[0].message.content

    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1:
        content = content[start:end + 1]

    return json.loads(content)