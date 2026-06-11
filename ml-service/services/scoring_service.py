def calculate_competition_score(
    cluster_size,
    avg_similarity
):

    score = (

        cluster_size * 1.5

        +

        avg_similarity * 50
    )

    score = min(
        score,
        100
    )

    if score >= 70:
        level = "High"

    elif score >= 40:
        level = "Medium"

    else:
        level = "Low"

    return {
        "score": round(score, 2),
        "level": level
    }


def calculate_differentiation_score(
    avg_similarity
):

    score = (

        100

        -

        (
            avg_similarity
            * 100
        )
    )

    return round(
        max(
            0,
            min(
                score,
                100
            )
        ),
        2
    )


def calculate_opportunity_score(

    competition_score,
    opportunity_count,
    risk_count,
    missing_feature_count
):

    score = (
    100
    - competition_score * 0.6
    + opportunity_count * 7
    - risk_count * 6
    + missing_feature_count * 2
   )

    return round(

        max(
            0,
            min(
                score,
                100
            )
        ),

        2
    )