import joblib
import pandas as pd

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    mean_absolute_error,
    r2_score
)

from xgboost import (
    XGBRegressor
)

df = pd.read_csv(
    "opportunity_dataset.csv"
)

X = df[

    [
        "competitor_count",
        "avg_similarity",
        "opportunity_count",
        "risk_count",
        "missing_feature_count"
    ]

]

y = df[
    "target_score"
]

X_train, X_test, y_train, y_test = (

    train_test_split(

        X,
        y,

        test_size=0.2,

        random_state=42
    )
)

model = XGBRegressor(

    n_estimators=300,

    max_depth=6,

    learning_rate=0.05,

    random_state=42
)

model.fit(
    X_train,
    y_train
)

preds = model.predict(
    X_test
)

print(
    "MAE:",
    mean_absolute_error(
        y_test,
        preds
    )
)

print(
    "R2:",
    r2_score(
        y_test,
        preds
    )
)

joblib.dump(
    model,
    "models/opportunity_model.pkl"
)

print(
    "Model Saved"
)