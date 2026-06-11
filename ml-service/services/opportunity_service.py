def calculate_opportunity(
    competitors,
    gap_analysis
):

    competitor_count = len(
        competitors
    )

    opportunities = len(
        gap_analysis.get(
            "opportunities",
            []
        )
    )

    risks = len(
        gap_analysis.get(
            "risks",
            []
        )
    )

    if competitor_count >= 8:

        competition_density = "High"

    elif competitor_count >= 4:

        competition_density = "Medium"

    else:

        competition_density = "Low"

    competition_penalty = (
    competitor_count * 4
    )

    opportunity_bonus = (
        opportunities * 10
    )

    risk_penalty = (
        risks * 6
    )

    score = (

        70

        + opportunity_bonus

        - risk_penalty

        - competition_penalty

    )

    score = max(
    0,
    min(score,100)
  )

    confidence = min(
        100,
        40 + competitor_count * 5
    )

    return {

        "competition_density":
            competition_density,

        "market_saturation":
            gap_analysis.get(
                "market_saturation",
                "Unknown"
            ),

        "opportunity_score":
            round(score, 2),

        "confidence":
            confidence,

        "strengths":
            gap_analysis.get(
                "opportunities",
                []
            ),

        "weaknesses":
            gap_analysis.get(
                "risks",
                []
            )
    }