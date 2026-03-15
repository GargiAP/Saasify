import pandas as pd
import numpy as np
import shap
import pickle
import json
import os
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

FEATURE_COLS = [
    "competition_density",
    "novelty_score",
    "market_growth",
    "pain_severity",
    "monetization_signal",
    "description_quality",
    "topic_diversity"
]

# weights based on startup research
# competition hurts, everything else helps
WEIGHTS = {
    "pain_severity":        0.25,
    "market_growth":        0.20,
    "monetization_signal":  0.20,
    "description_quality":  0.15,
    "novelty_score":        0.10,
    "topic_diversity":      0.05,
    "competition_density": -0.15
}

def compute_viability(row):
    score = sum(
        WEIGHTS[feat] * row[feat]
        for feat in FEATURE_COLS
    )
    return float(np.clip(score, 0, 1))

def train():
    print("Loading data...")
    df = pd.read_csv("data/training_data.csv")

    X = df[FEATURE_COLS].copy()

    # generate labels using our weighted formula
    # this IS our model — XGBoost learns to replicate it
    # and SHAP explains which features drive each prediction
    print("Computing viability scores...")
    y = df.apply(compute_viability, axis=1)

    print(f"Score range: {y.min():.3f} to {y.max():.3f}")
    print(f"Score mean:  {y.mean():.3f}")
    print(f"Score std:   {y.std():.3f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"\nTraining XGBoost to replicate scoring formula...")
    model = XGBRegressor(
        n_estimators=500,
        max_depth=4,
        learning_rate=0.02,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        verbosity=0
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, 0, 1)

    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\n========== MODEL EVALUATION ==========")
    print(f"R² score:          {r2:.4f}")
    print(f"MAE:               {mae:.4f}")
    print(f"MAE (0-100 scale): {mae*100:.2f} points")

    print(f"\n========== SHAP EXPLAINABILITY ==========")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    importance = pd.DataFrame({
        "feature": FEATURE_COLS,
        "mean_shap": np.abs(shap_values).mean(axis=0)
    }).sort_values("mean_shap", ascending=False)

    print("Feature importance:")
    for _, row in importance.iterrows():
        bar = "█" * int(row["mean_shap"] * 500)
        print(f"  {row['feature']:<25} {bar} {row['mean_shap']:.4f}")

    print(f"\n========== SAMPLE PREDICTIONS ==========\n")
    sample_ideas = [
        {
            "name": "Crowded AI tool, weak description",
            "competition_density": 0.8,
            "novelty_score": 0.2,
            "market_growth": 0.6,
            "pain_severity": 0.3,
            "monetization_signal": 0.3,
            "description_quality": 0.3,
            "topic_diversity": 0.4
        },
        {
            "name": "Niche developer tool, strong case",
            "competition_density": 0.2,
            "novelty_score": 0.8,
            "market_growth": 0.7,
            "pain_severity": 0.7,
            "monetization_signal": 0.6,
            "description_quality": 0.8,
            "topic_diversity": 0.6
        },
        {
            "name": "Generic productivity app",
            "competition_density": 0.5,
            "novelty_score": 0.4,
            "market_growth": 0.3,
            "pain_severity": 0.2,
            "monetization_signal": 0.2,
            "description_quality": 0.3,
            "topic_diversity": 0.3
        },
        {
            "name": "Unique fintech B2B tool",
            "competition_density": 0.3,
            "novelty_score": 0.7,
            "market_growth": 0.8,
            "pain_severity": 0.6,
            "monetization_signal": 0.8,
            "description_quality": 0.7,
            "topic_diversity": 0.7
        }
    ]

    for idea in sample_ideas:
        features = pd.DataFrame([{
            col: idea[col] for col in FEATURE_COLS
        }])
        
        raw = float(np.clip(model.predict(features)[0], 0, 1))
        score_100 = int(raw * 100)
        
        idea_shap = explainer.shap_values(features)[0]
        contributions = sorted(
            zip(FEATURE_COLS, idea_shap),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        print(f"  Idea: {idea['name']}")
        print(f"  Viability score: {score_100}/100")
        print(f"  Breakdown:")
        for feat, val in contributions[:4]:
            arrow = "▲" if val > 0 else "▼"
            direction = "helps" if val > 0 else "hurts"
            print(f"    {arrow} {feat:<25} {direction} ({val:+.3f})")
        print()

    # save
    os.makedirs("models", exist_ok=True)
    with open("models/viability_model.pkl", "wb") as f:
        pickle.dump(model, f)
    with open("models/shap_explainer.pkl", "wb") as f:
        pickle.dump(explainer, f)
    with open("models/feature_cols.pkl", "wb") as f:
        pickle.dump(FEATURE_COLS, f)
    with open("models/weights.json", "w") as f:
        json.dump(WEIGHTS, f, indent=2)

    metrics = {
        "model_type": "XGBoost Regressor",
        "approach": "formula-derived targets with SHAP explainability",
        "r2_score": round(r2, 4),
        "mae": round(mae, 4),
        "mae_100_scale": round(mae * 100, 2),
        "features": FEATURE_COLS,
        "weights": WEIGHTS
    }
    with open("models/metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("=" * 45)
    print(f"R²: {r2:.3f} | MAE: {mae*100:.1f} pts on 0-100 scale")
    print(f"\nAll models saved to models/")

    return model, explainer, metrics

if __name__ == "__main__":
    train()