"""
ml_model.py
Machine Learning — Predict Positive Outcome for Animals
Models: Random Forest, Gradient Boosting, Logistic Regression
Includes: Cross-validation, ROC-AUC, Feature Importance, Model Export
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os, pickle, warnings
warnings.filterwarnings("ignore")

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, roc_auc_score, roc_curve,
    precision_recall_curve, average_precision_score
)
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(CHARTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)


# ── Feature Engineering ────────────────────────────────────────────────────────

def build_ml_dataset(df_intakes: pd.DataFrame, df_outcomes: pd.DataFrame) -> pd.DataFrame:
    """Merge intakes + outcomes and engineer features for ML."""
    intake_cols = [
        "Animal ID", "Animal Type", "Intake Type", "Intake Condition",
        "Age_Months", "Sex", "Neutered", "Mixed_Breed",
        "Month", "Hour", "DayOfWeek"
    ]

    outcome_cols = [
        "Animal ID", "Outcome Type", "Positive_Outcome", "Outcome_Group"
    ]

    intake_cols = [c for c in intake_cols if c in df_intakes.columns]
    outcome_cols = [c for c in outcome_cols if c in df_outcomes.columns]

    df = pd.merge(
        df_intakes[intake_cols],
        df_outcomes[outcome_cols],
        on="Animal ID",
        how="inner"
    )

    df.sort_values("Animal ID", inplace=True)
    df.drop_duplicates(subset="Animal ID", keep="first", inplace=True)

    print(f"  ML dataset shape: {df.shape}")
    print(f"  Positive outcome rate: {df['Positive_Outcome'].mean():.1%}")

    return df


def encode_features(df: pd.DataFrame):
    """Label-encode categorical columns; return X, y, and encoder dict."""
    cat_cols = [
        "Animal Type",
        "Intake Type",
        "Intake Condition",
        "Sex",
        "DayOfWeek"
    ]

    cat_cols = [c for c in cat_cols if c in df.columns]

    le_dict = {}
    df_enc = df.copy()

    for col in cat_cols:
        le = LabelEncoder()
        df_enc[col + "_enc"] = le.fit_transform(df_enc[col].astype(str))
        le_dict[col] = le

    bool_cols = [c for c in ["Neutered", "Mixed_Breed"] if c in df_enc.columns]

    for col in bool_cols:
        df_enc[col + "_int"] = df_enc[col].astype(int)

    feature_cols = (
        [c + "_enc" for c in cat_cols] +
        [c + "_int" for c in bool_cols] +
        [c for c in ["Age_Months", "Month", "Hour"] if c in df_enc.columns]
    )

    df_model = df_enc[feature_cols + ["Positive_Outcome"]].dropna()

    X = df_model[feature_cols]
    y = df_model["Positive_Outcome"]

    print(f"  Features: {feature_cols}")
    print(f"  X shape: {X.shape}  |  Class balance: {dict(y.value_counts())}")

    return X, y, le_dict, feature_cols


# ── Training ───────────────────────────────────────────────────────────────────

def train_all_models(X_train, y_train):
    models = {
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.08,
            max_depth=5,
            subsample=0.8,
            random_state=42
        ),
        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                max_iter=500,
                class_weight="balanced",
                random_state=42,
                C=0.5
            ))
        ])
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    trained = {}

    print("\n🤖 Training models...\n" + "=" * 55)

    for name, model in models.items():
        model.fit(X_train, y_train)

        cv_scores = cross_val_score(
            model,
            X_train,
            y_train,
            cv=skf,
            scoring="roc_auc",
            n_jobs=-1
        )

        trained[name] = {
            "model": model,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std()
        }

        print(f"  {name:<25} CV AUC: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

    return trained


# ── Evaluation ─────────────────────────────────────────────────────────────────

def evaluate_models(trained, X_test, y_test, feature_cols):
    results = {}

    print("\n📊 Test Set Evaluation\n" + "=" * 55)

    for name, info in trained.items():
        model = info["model"]

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        acc = accuracy_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)
        ap = average_precision_score(y_test, y_prob)

        results[name] = {
            **info,
            "acc": acc,
            "auc": auc,
            "ap": ap,
            "y_pred": y_pred,
            "y_prob": y_prob
        }

        print(f"\n  {name}")
        print(f"    Accuracy : {acc:.3f}")
        print(f"    ROC-AUC  : {auc:.3f}")
        print(f"    Avg Prec : {ap:.3f}")
        print(f"    CV AUC   : {info['cv_mean']:.3f} ± {info['cv_std']:.3f}")

    best_name = max(results, key=lambda k: results[k]["auc"])

    print(f"\n  🏆 Best model: {best_name} (AUC={results[best_name]['auc']:.3f})")

    print(f"\n  Classification Report — {best_name}:")
    print(classification_report(
        y_test,
        results[best_name]["y_pred"],
        target_names=["Not Positive", "Positive"]
    ))

    return results, best_name


# ── Plotting ───────────────────────────────────────────────────────────────────

def plot_ml_results(results, best_name, X_test, y_test, feature_cols):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    colors = ["#4472C4", "#ED7D31", "#70AD47"]

    ax = axes[0, 0]
    for (name, res), color in zip(results.items(), colors):
        fpr, tpr, _ = roc_curve(y_test, res["y_prob"])
        ax.plot(
            fpr,
            tpr,
            label=f"{name} (AUC={res['auc']:.3f})",
            color=color,
            linewidth=2.2
        )

    ax.plot([0, 1], [0, 1], "k--", alpha=0.4, label="Random")
    ax.set_title("ROC Curves — All Models", fontsize=13, fontweight="bold")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[0, 1]
    for (name, res), color in zip(results.items(), colors):
        prec, rec, _ = precision_recall_curve(y_test, res["y_prob"])
        ax.plot(
            rec,
            prec,
            label=f"{name} (AP={res['ap']:.3f})",
            color=color,
            linewidth=2.2
        )

    ax.set_title("Precision-Recall Curves", fontsize=13, fontweight="bold")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    ax = axes[1, 0]
    cm = confusion_matrix(y_test, results[best_name]["y_pred"])
    cm_pct = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100

    annot = np.array([
        [f"{v:,}\n({p:.1f}%)" for v, p in zip(row_v, row_p)]
        for row_v, row_p in zip(cm, cm_pct)
    ])

    sns.heatmap(
        cm,
        ax=ax,
        annot=annot,
        fmt="",
        cmap="Blues",
        xticklabels=["Not Positive", "Positive"],
        yticklabels=["Not Positive", "Positive"],
        linewidths=0.5,
        cbar=False
    )

    ax.set_title(f"Confusion Matrix — {best_name}", fontsize=13, fontweight="bold")
    ax.set_ylabel("Actual")
    ax.set_xlabel("Predicted")

    ax = axes[1, 1]
    if "Random Forest" in results:
        rf = results["Random Forest"]["model"]

        importances = pd.Series(
            rf.feature_importances_,
            index=feature_cols
        ).sort_values(ascending=True)

        colors_imp = plt.cm.Blues(np.linspace(0.3, 0.9, len(importances)))

        importances.plot(
            kind="barh",
            ax=ax,
            color=colors_imp,
            edgecolor="white"
        )

        ax.set_title("Feature Importance — Random Forest", fontsize=13, fontweight="bold")
        ax.set_xlabel("Importance Score")
        ax.grid(axis="x", alpha=0.3)

    plt.suptitle(
        "ML Model Evaluation\nPredicting Positive Outcome (Adoption / Return to Owner)",
        fontsize=15,
        fontweight="bold",
        y=1.01
    )

    plt.tight_layout()

    path = os.path.join(CHARTS_DIR, "07_ml_evaluation.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.show()

    print(f"✅ ML chart saved → {path}")


# ── Export Model ───────────────────────────────────────────────────────────────

def save_best_model(results, best_name, le_dict, feature_cols):
    artifact = {
        "model": results[best_name]["model"],
        "le_dict": le_dict,
        "feature_cols": feature_cols,
        "auc": results[best_name]["auc"],
        "saved_at": pd.Timestamp.now().isoformat()
    }

    path = os.path.join(MODELS_DIR, "best_model.pkl")

    with open(path, "wb") as f:
        pickle.dump(artifact, f)

    print(f"✅ Best model saved → {path}")

    return path


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from data_cleaning import clean_intakes, clean_outcomes
    import sys

    DATA_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE_DIR, "data")

    print("Loading data...")

    df_i = pd.read_csv(
        os.path.join(DATA_PATH, "Austin_Animal_Center_Intakes.csv")
    )

    df_o = pd.read_csv(
        os.path.join(DATA_PATH, "Austin_Animal_Center_Outcomes.csv")
    )

    df_i_clean = clean_intakes(df_i)
    df_o_clean = clean_outcomes(df_o)

    df_ml = build_ml_dataset(df_i_clean, df_o_clean)

    X, y, le_dict, feature_cols = encode_features(df_ml)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    trained = train_all_models(X_train, y_train)

    results, best_name = evaluate_models(
        trained,
        X_test,
        y_test,
        feature_cols
    )

    plot_ml_results(
        results,
        best_name,
        X_test,
        y_test,
        feature_cols
    )

    save_best_model(
        results,
        best_name,
        le_dict,
        feature_cols
    )