import joblib
import shap
import pandas as pd

model = joblib.load(
    "models/xgboost_model.pkl"
)

explainer = shap.TreeExplainer(
    model
)


def explain_prediction(
    features
):

    df = pd.DataFrame(
        [features]
    )

    shap_values = (
        explainer.shap_values(df)
    )

    explanations = []

    for i, feature in enumerate(
        df.columns
    ):

        explanations.append({

            "feature":
                feature,

            "impact":
                round(
                    float(
                        shap_values[0][i]
                    ),
                    3
                )
        })

    explanations.sort(
        key=lambda x:
        abs(
            x["impact"]
        ),
        reverse=True
    )

    return explanations