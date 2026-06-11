from services.embedder import (
    generate_embedding
)

from services.idea_enrichment_service import (
    enrich_idea
)

from services.text_similarity_service import (
    semantic_similarity
)

from database.qdrant_db import (
    client
)


def similarity_bonus(
    idea_value,
    startup_value
):

    if not idea_value:
        return 0

    if not startup_value:
        return 0

    idea_value = (
        idea_value.lower()
    )

    startup_value = (
        startup_value.lower()
    )

    if idea_value == startup_value:
        return 10

    if (
        idea_value in startup_value
        or
        startup_value in idea_value
    ):
        return 5

    return 0


def find_competitors(
    idea,
    limit=20,
    idea_meta=None
):

    if idea_meta is None:

        print(
            "Classifying idea..."
        )

        idea_meta = (
            enrich_idea(
                idea
            )
        )

        print(
            idea_meta
        )

    vector = (
        generate_embedding(
            idea
        )
    )

    results = (
        client.query_points(
            collection_name="startups",
            query=vector,
            limit=limit
        )
    )

    competitors = []

    for result in results.points:

        payload = (
            result.payload
        )

        score = (
            result.score
            * 60
        )

        reasons = []
        match_reasons = []

        # -------------------
        # Industry Match
        # -------------------

        industry_match = int(

            similarity_bonus(

                idea_meta.get(
                    "industry",
                    ""
                ),

                payload.get(
                    "industry",
                    ""
                )

            ) > 0
        )

        if industry_match:

            score += 10

            reasons.append(
                "Same industry"
            )

            match_reasons.append(
                "Operates in same industry"
            )

        # -------------------
        # Subcategory Match
        # -------------------

        subcategory_match = int(

            similarity_bonus(

                idea_meta.get(
                    "subcategory",
                    ""
                ),

                payload.get(
                    "subcategory",
                    ""
                )

            ) > 0
        )

        if subcategory_match:

            score += 15

            reasons.append(
                "Same subcategory"
            )

            match_reasons.append(
                "Same product category"
            )

        # -------------------
        # Customer Similarity
        # -------------------

        customer_similarity = (
            semantic_similarity(

                idea_meta.get(
                    "target_customer",
                    ""
                ),

                payload.get(
                    "target_customer",
                    ""
                )

            )
        )

        if customer_similarity > 0.60:

            score += (
                customer_similarity
                * 10
            )

            reasons.append(
                f"Similar customer ({round(customer_similarity,2)})"
            )

        if customer_similarity > 0.70:

            match_reasons.append(
                "Targets similar customers"
            )

        # -------------------
        # Business Model
        # -------------------

        if similarity_bonus(

            idea_meta.get(
                "business_model",
                ""
            ),

            payload.get(
                "business_model",
                ""
            )

        ):

            score += 5

            reasons.append(
                "Same business model"
            )

            match_reasons.append(
                "Uses same business model"
            )

        # -------------------
        # Pain Similarity
        # -------------------

        pain_similarity = (
            semantic_similarity(

                idea_meta.get(
                    "pain_point",
                    ""
                ),

                payload.get(
                    "pain_point",
                    ""
                )

            )
        )

        if pain_similarity > 0.60:

            score += (
                pain_similarity
                * 20
            )

            reasons.append(
                f"Similar pain point ({round(pain_similarity,2)})"
            )

        if pain_similarity > 0.70:

            match_reasons.append(
                "Solves similar problem"
            )

        # -------------------
        # Solution Similarity
        # -------------------

        solution_similarity = (
            semantic_similarity(

                idea_meta.get(
                    "solution",
                    ""
                ),

                payload.get(
                    "solution",
                    ""
                )

            )
        )

        if solution_similarity > 0.60:

            score += (
                solution_similarity
                * 20
            )

            reasons.append(
                f"Similar solution ({round(solution_similarity,2)})"
            )

        if solution_similarity > 0.70:

            match_reasons.append(
                "Uses similar solution"
            )

        score = min(
            round(score, 2),
            100
        )

        competitors.append({

            "startup_id":
                result.id,

            "name":
                payload.get(
                    "name",
                    ""
                ),

            "industry":
                payload.get(
                    "industry",
                    ""
                ),

            "subcategory":
                payload.get(
                    "subcategory",
                    ""
                ),

            "target_customer":
                payload.get(
                    "target_customer",
                    ""
                ),

            "business_model":
                payload.get(
                    "business_model",
                    ""
                ),

            "pain_point":
                payload.get(
                    "pain_point",
                    ""
                ),

            "solution":
                payload.get(
                    "solution",
                    ""
                ),

            "pain_similarity":
                round(
                    pain_similarity,
                    4
                ),

            "solution_similarity":
                round(
                    solution_similarity,
                    4
                ),

            "customer_similarity":
                round(
                    customer_similarity,
                    4
                ),

            "industry_match":
                industry_match,

            "subcategory_match":
                subcategory_match,

            "score":
                score,

            "reasons":
                reasons,

            "match_reasons":
                match_reasons
        })

    competitors.sort(
        key=lambda x:
        x["score"],
        reverse=True
    )

    return competitors[:10]