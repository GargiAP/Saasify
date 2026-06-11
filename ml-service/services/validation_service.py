from services.gap_analysis_service import (
    analyze_market_gap
)

from services.competitor_service import (
    find_competitors
)


def calculate_validation_score(
    idea
):

    competitors = find_competitors(
        idea
    )

    gap_analysis = analyze_market_gap(
        idea
    )

    competitor_count = len(
        competitors
    )

    # Competition score

    competition_score = max(
        0,
        100 - (competitor_count * 5)
    )

    # Opportunity score

    opportunity_score = min(
        100,
        len(
            gap_analysis[
                "opportunities"
            ]
        ) * 30
    )

    # Novelty score

    if (
        gap_analysis[
            "market_saturation"
        ].lower()
        == "high"
    ):
        novelty_score = 60

    elif (
        gap_analysis[
            "market_saturation"
        ].lower()
        == "medium"
    ):
        novelty_score = 75

    else:
        novelty_score = 90

    # Execution score

    execution_score = 75

    overall_score = round(

        (
            competition_score
            +
            opportunity_score
            +
            novelty_score
            +
            execution_score
        )
        / 4,

        2
    )

    return {

        "overall_score":
            overall_score,

        "competition_score":
            competition_score,

        "opportunity_score":
            opportunity_score,

        "novelty_score":
            novelty_score,

        "execution_score":
            execution_score
    }