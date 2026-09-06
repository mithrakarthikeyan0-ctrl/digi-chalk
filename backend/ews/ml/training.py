import os
import joblib
import pandas as pd
from django.conf import settings
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score
from ews.models import ModelVersion

# EWS Model Storage Path
MODEL_DIR = os.path.join(settings.BASE_DIR, 'ews', 'ml', 'saved_models')
os.makedirs(MODEL_DIR, exist_ok=True)

def train_baseline_model(version_name, df, use_rf=False):
    """
    Trains a simple Logistic Regression (or Random Forest) EWS model on the provided dataframe.
    `df` must contain the target column 'needs_intervention' and feature columns.
    """
    features = [
        'attendance_rate',
        'late_attendance_count',
        'lesson_replay_completion',
        'quiz_score_avg',
        'recent_engagement_score',
        'session_participation_count',
        'trend_vs_previous'
    ]
    
    X = df[features]
    y = df['needs_intervention']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    if use_rf:
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        algorithm = 'RandomForest'
    else:
        model = LogisticRegression(random_state=42, max_iter=1000)
        algorithm = 'LogisticRegression'

    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "support": int(len(y_test))
    }
    
    # Save model
    model_path = os.path.join(MODEL_DIR, f"{version_name}.pkl")
    joblib.dump(model, model_path)
    
    # Create DB entry (Admin must activate it later)
    model_version = ModelVersion.objects.create(
        version_name=version_name,
        algorithm=algorithm,
        training_data_description=f"Synthetic/Uploaded dataset with {len(df)} records.",
        feature_schema_version='v1.0',
        training_metrics=metrics,
        approval_status=ModelVersion.Status.DRAFT
    )
    
    return model_version
