import numpy as np

from services.embedder import (
    generate_embedding
)


def cosine_similarity(
    vec1,
    vec2
):

    vec1 = np.array(
        vec1
    )

    vec2 = np.array(
        vec2
    )

    return float(

        np.dot(
            vec1,
            vec2
        )

        /

        (

            np.linalg.norm(
                vec1
            )

            *

            np.linalg.norm(
                vec2
            )

        )
    )


def semantic_similarity(
    text1,
    text2
):

    if not text1:
        return 0

    if not text2:
        return 0

    vec1 = (
        generate_embedding(
            text1
        )
    )

    vec2 = (
        generate_embedding(
            text2
        )
    )

    return cosine_similarity(
        vec1,
        vec2
    )