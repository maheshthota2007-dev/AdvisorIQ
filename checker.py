import pandas as pd
import joblib
from pathlib import Path

FEATURES = ["amount", "hour", "is_foreign", "merchant_risk"]

MODEL_PATH = "models/checker.joblib"


def train(csv="data/sample_transactions.csv"):

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score

    df = pd.read_csv(csv)

    X = df[FEATURES]
    y = df["is_suspicious"]

    Xtr, Xte, ytr, yte = train_test_split(
        X,
        y,
        test_size=0.2,
        stratify=y,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42
    )

    model.fit(Xtr, ytr)

    predictions = model.predict(Xte)

    print("Classification Report:")
    print(classification_report(yte, predictions))

    print(
        "ROC-AUC:",
        roc_auc_score(
            yte,
            model.predict_proba(Xte)[:, 1]
        )
    )

    Path(MODEL_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(model, MODEL_PATH)

    print()
    print("Model saved to:", MODEL_PATH)


def flag_transactions(df: pd.DataFrame):

    model = joblib.load(MODEL_PATH)

    scores = model.predict_proba(
        df[FEATURES]
    )[:, 1]

    df = df.assign(
        risk_score=scores
    )

    return df[
        df.risk_score > 0.5
    ].sort_values(
        "risk_score",
        ascending=False
    )


if __name__ == "__main__":
    train()