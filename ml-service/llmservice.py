from groq import Groq
import json
import os
import re
import time
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def call_llm(prompt: str, max_tokens: int = 1000) -> str:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def preprocess_idea(raw_idea: str) -> dict:
    prompt = f"""You are an expert startup analyst. A founder submitted this idea:

"{raw_idea}"

Extract and return a JSON object with exactly these fields:
{{
  "cleaned_idea": "one clear sentence describing the core idea",
  "problem_being_solved": "what pain point this addresses",
  "target_audience": "who the primary users are",
  "core_value_proposition": "the main benefit in one sentence",
  "market_category": "one of: Developer Tools, AI Tools, Marketing Tools, Productivity Tools, Creator Tools, Fintech, Health Tech, E-commerce, Education, Other",
  "keywords": ["3", "to", "5", "relevant", "keywords"]
}}

Return ONLY the JSON object. No explanation, no markdown, no extra text."""

    response_text = call_llm(prompt, max_tokens=500)

    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    response_text = response_text.strip()

    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        return {
            "cleaned_idea": raw_idea,
            "problem_being_solved": "unclear",
            "target_audience": "unclear",
            "core_value_proposition": "unclear",
            "market_category": "Other",
            "keywords": []
        }

def generate_report(
    idea_info: dict,
    similar_products: list,
    gap_analysis: dict,
    viability_score: int,
    shap_breakdown: list
) -> str:

    shap_text = "\n".join([
        f"- {feat}: {'helps' if val > 0 else 'hurts'} ({val:+.3f})"
        for feat, val in shap_breakdown[:4]
    ])

    competitors_text = "\n".join([
        f"- {p['name']}: {p['tagline']} (similarity: {p['similarity']})"
        for p in similar_products[:5]
    ])

    gaps_text = "\n".join([
        f"- {gap}"
        for gap in gap_analysis.get("gaps", [])[:4]
    ])

    opportunities_text = "\n".join([
        f"- {opp}"
        for opp in gap_analysis.get("opportunities", [])[:3]
    ])

    prompt = f"""You are Saasify, an expert startup idea analyst.
Generate a concise, actionable analysis report for this startup idea.

IDEA INFORMATION:
- Idea: {idea_info.get('cleaned_idea')}
- Problem: {idea_info.get('problem_being_solved')}
- Target audience: {idea_info.get('target_audience')}
- Market category: {idea_info.get('market_category')}

SIMILAR PRODUCTS FOUND:
{competitors_text}

MARKET GAPS DETECTED:
{gaps_text}

OPPORTUNITY DIRECTIONS:
{opportunities_text}

VIABILITY SCORE: {viability_score}/100

SCORE BREAKDOWN:
{shap_text}

CROWDING LEVEL: {gap_analysis.get('crowding_level', 'Medium')}

Write a report with exactly these sections:
1. IDEA SUMMARY (2 sentences)
2. MARKET LANDSCAPE (2-3 sentences about competition)
3. KEY GAPS AND OPPORTUNITIES (3 bullet points)
4. VIABILITY ASSESSMENT (2 sentences explaining the score)
5. WHAT TO VALIDATE NEXT (3 specific actionable steps)

Be direct, specific, and honest. No fluff. Talk like a senior investor."""

    return call_llm(prompt, max_tokens=1000)

def analyze_idea_with_llm(
    raw_idea: str,
    similar_products: list,
    gap_analysis: dict,
    viability_score: int,
    shap_breakdown: list
) -> dict:

    print("Step 1: Preprocessing idea with LLM...")
    idea_info = preprocess_idea(raw_idea)
    print(f"Cleaned idea: {idea_info.get('cleaned_idea')}")
    print(f"Market:       {idea_info.get('market_category')}")

    time.sleep(1)

    print("Step 2: Generating analysis report...")
    report = generate_report(
        idea_info,
        similar_products,
        gap_analysis,
        viability_score,
        shap_breakdown
    )

    return {
        "idea_info": idea_info,
        "report": report
    }

if __name__ == "__main__":
    test_idea = "an app that helps content creators find viral video ideas using AI"

    test_similar = [
        {"name": "SEONIB",
         "tagline": "Turn trending topics into SEO traffic",
         "similarity": 0.462},
        {"name": "MomentSurfer",
         "tagline": "AI Scrolling Agent",
         "similarity": 0.447},
        {"name": "Cortiq",
         "tagline": "AI co-founder for startup ideas",
         "similarity": 0.447}
    ]

    test_gaps = {
        "gaps": [
            "viral video discovery",
            "content ideation",
            "trend prediction"
        ],
        "opportunities": [
            "Build around viral video discovery — competitors not focusing here",
            "Focus on pre-creation workflow — competitors focus on post-publishing",
            "Market is crowded overall — niche down to specific creator type"
        ],
        "crowding_level": "High"
    }

    test_shap = [
        ("pain_severity", 0.045),
        ("market_growth", 0.038),
        ("competition_density", -0.032),
        ("monetization_signal", 0.021)
    ]

    result = analyze_idea_with_llm(
        test_idea,
        test_similar,
        test_gaps,
        viability_score=42,
        shap_breakdown=test_shap
    )

    print("\n========== IDEA INFO ==========")
    print(json.dumps(result["idea_info"], indent=2))

    print("\n========== ANALYSIS REPORT ==========")
    print(result["report"])