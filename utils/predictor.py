import os
import joblib
import numpy as np
import pandas as pd
from config import Config


class PredictorEngine:
    """
    Inference Engine for loading serialized GTU grade prediction model,
    formatting input payloads, and executing prediction pipelines.
    """

    _model = None

    @classmethod
    def load_model(cls):
        """Lazy load model pipeline from disk."""
        if cls._model is None:
            if not os.path.exists(Config.MODEL_PATH):
                raise FileNotFoundError(
                    f"Model file not found at {Config.MODEL_PATH}. Train the model first."
                )
            cls._model = joblib.load(Config.MODEL_PATH)
            print(f"[PredictorEngine] Model loaded successfully from {Config.MODEL_PATH}")
        return cls._model

    @classmethod
    def predict(cls, data):
        """
        Executes prediction on input dictionary.
        
        Expected payload keys:
        - department (str)
        - semester (int/str)
        - subject (str)
        - assessment_stage (str)
        - attendance_pct (float)
        - spi_last_sem (float)
        - weekly_study_hours (float)
        - active_backlogs (int)
        - mid1_marks (float or None)
        - mid2_marks (float or None)
        """
        model = cls.load_model()

        dept = str(data.get("department", "")).strip()
        sem = str(data.get("semester", "")).strip()
        subject = str(data.get("subject", "")).strip()
        stage = str(data.get("assessment_stage", "")).strip()

        attendance = float(data.get("attendance_pct", 0.0))
        spi = float(data.get("spi_last_sem", 0.0))
        study_hours = float(data.get("weekly_study_hours", 0.0))
        backlogs = int(data.get("active_backlogs", 0))

        # Handle stage-specific null marks
        mid1 = data.get("mid1_marks")
        mid2 = data.get("mid2_marks")

        if stage == "Before Mid-1":
            mid1_val = -1.0
            mid2_val = -1.0
        elif stage == "After Mid-1":
            mid1_val = float(mid1) if mid1 is not None else -1.0
            mid2_val = -1.0
        else:  # After Mid-2
            mid1_val = float(mid1) if mid1 is not None else -1.0
            mid2_val = float(mid2) if mid2 is not None else -1.0

        # Construct DataFrame matching trained pipeline columns
        input_df = pd.DataFrame(
            [
                {
                    "Department": dept,
                    "Semester": sem,
                    "Subject": subject,
                    "Assessment Stage": stage,
                    "Attendance": float(attendance),
                    "SPI": float(spi),
                    "Study Hours": float(study_hours),
                    "Backlogs": float(backlogs),
                    "Mid1": float(mid1_val),
                    "Mid2": float(mid2_val),
                }
            ]
        )

        # Predict grade class
        predicted_grade = str(model.predict(input_df)[0])

        # Get class probabilities
        probabilities = model.predict_proba(input_df)[0]
        classes = list(model.classes_)

        # Calculate Pass Probability (100% - P(FF))
        if "FF" in classes:
            ff_idx = classes.index("FF")
            pass_probability = round(float((1.0 - probabilities[ff_idx]) * 100.0), 1)
        else:
            pass_probability = 95.0

        # Confidence Score (Max probability)
        confidence_score = round(float(np.max(probabilities) * 100.0), 1)

        # Performance Category Mapping
        if predicted_grade in ["AA", "AB"]:
            performance_category = "Excellent"
        elif predicted_grade in ["BB", "BC"]:
            performance_category = "Very Good" if predicted_grade == "BB" else "Good"
        elif predicted_grade in ["CC", "CD"]:
            performance_category = "Average"
        else:  # DD or FF
            performance_category = "At Risk"

        # Calculate feature contributions
        feature_contributions = cls._calculate_feature_contributions(
            attendance, spi, study_hours, backlogs, stage, mid1_val, mid2_val
        )

        return {
            "predicted_grade": predicted_grade,
            "pass_probability": pass_probability,
            "performance_category": performance_category,
            "confidence_score": confidence_score,
            "feature_contributions": feature_contributions,
        }

    @staticmethod
    def _calculate_feature_contributions(
        attendance, spi, study_hours, backlogs, stage, mid1, mid2
    ):
        """Determines top contributing factors and positive/negative impact."""
        factors = []

        # Attendance Impact
        if attendance >= 75.0:
            factors.append({"factor": "Attendance Rate", "value": f"{attendance:.1f}%", "impact": "Positive"})
        else:
            factors.append({"factor": "Attendance Rate", "value": f"{attendance:.1f}%", "impact": "Negative"})

        # SPI Impact
        if spi >= 6.5:
            factors.append({"factor": "Last Sem SPI", "value": f"{spi:.2f}", "impact": "Positive"})
        else:
            factors.append({"factor": "Last Sem SPI", "value": f"{spi:.2f}", "impact": "Negative"})

        # Study Hours Impact
        if study_hours >= 14.0:
            factors.append({"factor": "Weekly Study Hours", "value": f"{study_hours:.1f} hrs/wk", "impact": "Positive"})
        else:
            factors.append({"factor": "Weekly Study Hours", "value": f"{study_hours:.1f} hrs/wk", "impact": "Negative"})

        # Backlogs Impact
        if backlogs == 0:
            factors.append({"factor": "Active Backlogs", "value": "0 Backlogs", "impact": "Positive"})
        else:
            factors.append({"factor": "Active Backlogs", "value": f"{backlogs} Backlogs", "impact": "Negative"})

        # Mid-1 Impact
        if stage in ["After Mid-1", "After Mid-2"] and mid1 >= 0:
            if mid1 >= 6.0:
                factors.append({"factor": "Mid-1 Marks", "value": f"{mid1:.1f}/10", "impact": "Positive"})
            else:
                factors.append({"factor": "Mid-1 Marks", "value": f"{mid1:.1f}/10", "impact": "Negative"})

        # Mid-2 Impact
        if stage == "After Mid-2" and mid2 >= 0:
            if mid2 >= 12.0:
                factors.append({"factor": "Mid-2 Marks", "value": f"{mid2:.1f}/20", "impact": "Positive"})
            else:
                factors.append({"factor": "Mid-2 Marks", "value": f"{mid2:.1f}/20", "impact": "Negative"})

        return factors
