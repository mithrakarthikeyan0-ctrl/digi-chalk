import os
import joblib
import pandas as pd
from django.conf import settings

MODEL_DIR = os.path.join(settings.BASE_DIR, 'ews', 'ml', 'saved_models')

def run_inference(feature_snapshot, model_version):
    """
    Loads the approved model and runs inference on a single FeatureSnapshot.
    Returns (score_0_to_100, risk_band, top_contributing_factors)
    """
    model_path = os.path.join(MODEL_DIR, f"{model_version.version_name}.pkl")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found for version: {model_version.version_name}")
        
    model = joblib.load(model_path)
    
    feature_names = [
        'attendance_rate',
        'late_attendance_count',
        'lesson_replay_completion',
        'quiz_score_avg',
        'recent_engagement_score',
        'session_participation_count',
        'trend_vs_previous'
    ]
    
    X = pd.DataFrame([{
        'attendance_rate': feature_snapshot.attendance_rate,
        'late_attendance_count': feature_snapshot.late_attendance_count,
        'lesson_replay_completion': feature_snapshot.lesson_replay_completion,
        'quiz_score_avg': feature_snapshot.quiz_score_avg,
        'recent_engagement_score': feature_snapshot.recent_engagement_score,
        'session_participation_count': feature_snapshot.session_participation_count,
        'trend_vs_previous': feature_snapshot.trend_vs_previous
    }])
    
    # Probability of class 1 (needs intervention)
    prob = model.predict_proba(X)[0][1]
    score = prob * 100
    
    if score >= 75:
        risk_band = 'priority'
    elif score >= 50:
        risk_band = 'review'
    else:
        risk_band = 'routine'
        
    # Explainability: Top contributing factors (Directional feature importance)
    top_factors = {}
    
    if hasattr(model, 'coef_'):
        # Logistic Regression
        coefficients = model.coef_[0]
        # Calculate individual feature contributions: coef * value
        contributions = {name: coef * val for name, coef, val in zip(feature_names, coefficients, X.iloc[0])}
        # Sort by absolute contribution to find the top drivers
        sorted_factors = sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)
        top_factors = [{"feature": k, "contribution": v} for k, v in sorted_factors[:3]]
    elif hasattr(model, 'feature_importances_'):
        # Random Forest (Global feature importance, less specific to individual but works as fallback)
        importances = model.feature_importances_
        sorted_factors = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        top_factors = [{"feature": k, "global_importance": v} for k, v in sorted_factors[:3]]
        
    return score, risk_band, top_factors
