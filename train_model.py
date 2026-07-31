import datetime
import json
import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import Config


def load_dataset(file_path=Config.DATASET_PATH):
    """Load GTU student dataset from CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at {file_path}")

    df = pd.read_csv(file_path)
    # Strip any whitespace in column names
    df.columns = df.columns.str.strip()
    print(f"[ML] Dataset loaded successfully with {len(df)} records.")
    return df


def build_preprocessor(categorical_cols, numerical_cols):
    """
    Build scikit-learn ColumnTransformer for preprocessing.
    - Categorical features: OneHotEncoder
    - Numerical features: SimpleImputer (constant -1 for stage missingness) + StandardScaler
    """
    num_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="constant", fill_value=-1.0)),
            ("scaler", StandardScaler()),
        ]
    )

    cat_pipeline = Pipeline(
        [
            (
                "onehot",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numerical_cols),
            ("cat", cat_pipeline, categorical_cols),
        ]
    )

    return preprocessor


def train_and_evaluate_models(X_train, X_test, y_train, y_test, preprocessor):
    """
    Trains multiple classifiers, performs 5-fold cross-validation,
    evaluates on test split, and selects the best model.
    """
    candidate_models = {
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=200, max_depth=20, random_state=42, n_jobs=-1
        ),
        "ExtraTreesClassifier": ExtraTreesClassifier(
            n_estimators=200, max_depth=20, random_state=42, n_jobs=-1
        ),
        "HistGradientBoostingClassifier": HistGradientBoostingClassifier(
            max_iter=200, random_state=42
        ),
    }

    best_model_name = None
    best_pipeline = None
    best_f1 = -1.0
    best_metrics = {}
    model_results = {}

    print("\n[ML] Training and evaluating candidate models...\n" + "=" * 60)

    for name, model in candidate_models.items():
        pipeline = Pipeline(
            [("preprocessor", preprocessor), ("classifier", model)]
        )

        # 5-Fold Cross Validation on Training Data
        cv_scores = cross_val_score(
            pipeline, X_train, y_train, cv=5, scoring="f1_macro", n_jobs=-1
        )
        mean_cv_score = float(np.mean(cv_scores))

        # Fit full training set
        pipeline.fit(X_train, y_train)

        # Predict test set
        y_pred = pipeline.predict(X_test)

        acc = float(accuracy_score(y_test, y_pred))
        prec = float(
            precision_score(
                y_test, y_pred, average="macro", zero_division=0
            )
        )
        rec = float(
            recall_score(
                y_test, y_pred, average="macro", zero_division=0
            )
        )
        f1 = float(
            f1_score(y_test, y_pred, average="macro", zero_division=0)
        )

        model_results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1_score": f1,
            "cv_macro_f1": mean_cv_score,
            "pipeline": pipeline,
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "classification_report": classification_report(
                y_test, y_pred, output_dict=True, zero_division=0
            ),
        }

        print(
            f"Model: {name:<32} | Acc: {acc:.4f} | F1 (Macro): {f1:.4f} | CV F1: {mean_cv_score:.4f}"
        )

        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
            best_pipeline = pipeline
            best_metrics = model_results[name]

    print("=" * 60)
    print(
        f"[BEST MODEL SELECTED] {best_model_name} (Accuracy: {best_metrics['accuracy'] * 100:.2f}%, F1: {best_metrics['f1_score']:.4f})"
    )

    return best_model_name, best_pipeline, best_metrics, model_results


def save_model_and_metadata(
    model_name, pipeline, metrics, feature_cols, target_classes
):
    """Save trained pipeline to joblib and metadata to JSON."""
    os.makedirs(Config.MODELS_DIR, exist_ok=True)

    # Save Model Pipeline
    joblib.dump(pipeline, Config.MODEL_PATH)
    print(f"[ML] Trained model pipeline saved -> {Config.MODEL_PATH}")

    # Prepare Metadata
    metadata = {
        "version": "1.0.0",
        "model_name": model_name,
        "training_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "accuracy": round(metrics["accuracy"], 4),
        "precision_macro": round(metrics["precision"], 4),
        "recall_macro": round(metrics["recall"], 4),
        "f1_macro": round(metrics["f1_score"], 4),
        "cv_macro_f1": round(metrics["cv_macro_f1"], 4),
        "features": feature_cols,
        "target_classes": list(target_classes),
    }

    with open(Config.METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"[ML] Model metadata saved -> {Config.METADATA_PATH}")
    return metadata


def main():
    # 1. Load Data
    df = load_dataset()

    categorical_cols = [
        "Department",
        "Semester",
        "Subject",
        "Assessment Stage",
    ]
    numerical_cols = [
        "Attendance",
        "SPI",
        "Study Hours",
        "Backlogs",
        "Mid1",
        "Mid2",
    ]

    feature_cols = categorical_cols + numerical_cols
    target_col = "Expected Grade"

    X = df[feature_cols].copy()
    y = df[target_col]

    # Convert Semester to string for categorical encoding
    X["Semester"] = X["Semester"].astype(str)

    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 2. Build Preprocessor
    preprocessor = build_preprocessor(categorical_cols, numerical_cols)

    # 3. Train & Evaluate Models
    best_name, best_pipeline, best_metrics, _ = train_and_evaluate_models(
        X_train, X_test, y_train, y_test, preprocessor
    )

    # 4. Save Artifacts
    target_classes = sorted(y.unique())
    save_model_and_metadata(
        best_name, best_pipeline, best_metrics, feature_cols, target_classes
    )

    print("\n[ML Pipeline Complete] All models evaluated and exported.")


if __name__ == "__main__":
    main()
