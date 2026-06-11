import joblib
import pandas as pd

from services.shap_service import (
    explain_prediction
)

model = joblib.load(
    "models/xgboost_model.pkl"
)

feature_cols = joblib.load(
    "models/features.pkl"
)


def predict_viability(
    features
):

    df = pd.DataFrame(
        [features]
    )

    df = df[
        feature_cols
    ]

    prediction = (
        model.predict(df)[0]
    )

    prediction = max(
        0,
        min(
            100,
            float(prediction)
        )
    )

    shap_result = (
        explain_prediction(
            features
        )
    )

    return {

        "score":
            round(
                prediction,
                2
            ),

        "top_factors":
            shap_result[:5]
    }