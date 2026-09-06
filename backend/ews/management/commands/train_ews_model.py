import pandas as pd
import numpy as np
from django.core.management.base import BaseCommand
from ews.ml.training import train_baseline_model

class Command(BaseCommand):
    help = 'Trains the EWS model on synthetic data'

    def add_arguments(self, parser):
        parser.add_argument('--version_name', type=str, required=True, help='Name for this model version')
        parser.add_argument('--use_rf', action='store_true', help='Use Random Forest instead of Logistic Regression')
        parser.add_argument('--samples', type=int, default=1000, help='Number of synthetic samples to generate')

    def handle(self, *args, **options):
        version_name = options['version_name']
        use_rf = options['use_rf']
        samples = options['samples']
        
        self.stdout.write(f"Generating {samples} synthetic samples...")
        
        # Generate synthetic data with some correlation to 'needs_intervention'
        np.random.seed(42)
        data = {
            'attendance_rate': np.random.uniform(40, 100, samples),
            'late_attendance_count': np.random.randint(0, 10, samples),
            'lesson_replay_completion': np.random.uniform(0, 100, samples),
            'quiz_score_avg': np.random.uniform(20, 100, samples),
            'recent_engagement_score': np.random.uniform(0, 100, samples),
            'session_participation_count': np.random.randint(0, 20, samples),
            'trend_vs_previous': np.random.uniform(-20, 20, samples),
        }
        df = pd.DataFrame(data)
        
        # Define synthetic rule for ground truth
        # Lower attendance, lower engagement, negative trend = higher chance of intervention
        risk_score = (
            (100 - df['attendance_rate']) * 0.4 +
            df['late_attendance_count'] * 2 +
            (100 - df['recent_engagement_score']) * 0.3 -
            df['trend_vs_previous'] * 0.5
        )
        
        # Add some noise
        risk_score += np.random.normal(0, 5, samples)
        
        # Top 30% are marked as needing intervention
        threshold = np.percentile(risk_score, 70)
        df['needs_intervention'] = (risk_score > threshold).astype(int)
        
        self.stdout.write("Training model...")
        model_version = train_baseline_model(version_name, df, use_rf=use_rf)
        
        self.stdout.write(self.style.SUCCESS(f"Successfully trained and saved model version '{version_name}'"))
        self.stdout.write(f"Metrics: {model_version.training_metrics}")
        self.stdout.write("Note: This model is currently in DRAFT status and must be approved by an admin before use.")
