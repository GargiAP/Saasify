import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split
)

from sklearn.metrics import (
    r2_score,
    mean_absolute_error
)

from xgboost import (
    XGBRegressor
)

df = pd.read_csv(
    "real_training_data.csv"
)

X = df.drop(
    columns=["target"]
)

y = df["target"]

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

predictions = model.predict(
    X_test
)

print(
    "R2:",
    r2_score(
        y_test,
        predictions
    )
)

print(
    "MAE:",
    mean_absolute_error(
        y_test,
        predictions
    )
)

joblib.dump(
    model,
    "models/xgboost_model.pkl"
)

joblib.dump(
    list(X.columns),
    "models/features.pkl"
)

print(
    "Model saved successfully"
)