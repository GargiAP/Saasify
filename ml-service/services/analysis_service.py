from services.idea_enrichment_service import (
    enrich_idea
)

from services.competitor_service import (
    find_competitors
)

from services.gap_analysis_service import (
    analyze_market_gap
)

from services.recommendation_service import (
    generate_recommendations
)

from services.cluster_service import (
    analyze_cluster
)

from services.scoring_service import (
    calculate_competition_score,
    calculate_differentiation_score,
    calculate_opportunity_score
)


def analyze_startup_idea(
    idea
):

    # -------------------------
    # Enrich Idea
    # -------------------------

    idea_meta = enrich_idea(
        idea
    )

    # -------------------------
    # Competitors
    # -------------------------

    competitors = find_competitors(
        idea,
        idea_meta=idea_meta
    )

    # -------------------------
    # Gap Analysis
    # -------------------------

    gap_analysis = analyze_market_gap(
        idea,
        competitors,
        idea_meta
    )

    # -------------------------
    # Recommendations
    # -------------------------

    recommendations = generate_recommendations(
        idea,
        competitors,
        gap_analysis,
        idea_meta
    )

    # -------------------------
    # Cluster Intelligence
    # -------------------------

    cluster_analysis = analyze_cluster(
        idea,
        idea_meta=idea_meta
    )

    # -------------------------
    # Average Similarity
    # -------------------------

    similarities = []

    for competitor in competitors:

        similarity = (

            competitor.get(
                "pain_similarity",
                0
            )

            +

            competitor.get(
                "solution_similarity",
                0
            )

            +

            competitor.get(
                "customer_similarity",
                0
            )

        ) / 3

        similarities.append(
            similarity
        )

    avg_similarity = (

        sum(similarities)

        /

        len(similarities)

        if similarities

        else 0
    )

    # -------------------------
    # Competition Score
    # -------------------------

    competition = calculate_competition_score(

        cluster_analysis[
            "cluster_size"
        ],

        avg_similarity
    )

    # -------------------------
    # Differentiation Score
    # -------------------------

    differentiation_score = (

        calculate_differentiation_score(
            avg_similarity
        )
    )

    # -------------------------
    # Opportunity Score
    # -------------------------

    opportunity_score = (

        calculate_opportunity_score(

            competition[
                "score"
            ],

            len(
                gap_analysis.get(
                    "opportunities",
                    []
                )
            ),

            len(
                gap_analysis.get(
                    "risks",
                    []
                )
            ),

            len(
                gap_analysis.get(
                    "missing_features",
                    []
                )
            )
        )
    )

    return {

        "idea":
            idea,

        "idea_meta":
            idea_meta,

        "market_intelligence": {

            "market_segment":
                cluster_analysis[
                    "market_segment"
                ],

            "cluster_id":
                cluster_analysis[
                    "cluster_id"
                ],

            "cluster_size":
                cluster_analysis[
                    "cluster_size"
                ],

            "competition":
                competition,

            "differentiation_score":
                differentiation_score,

            "opportunity_score":
                opportunity_score
        },

        "competitors":
            competitors,

        "market_gap":
            gap_analysis,

        "recommendations":
            recommendations
    }